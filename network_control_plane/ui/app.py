"""
Control Plane Web Application

Minimal Flask web UI for network control plane operations.
Provides topology status, telemetry visibility, and control actions.
"""

import logging
import os
import tempfile
from flask import Flask, render_template, jsonify, request
from pathlib import Path
from werkzeug.utils import secure_filename

from ..desired_state import DesiredStateParser, DesiredStateError
from ..config_rendering import ConfigRenderer, ConfigRenderingError
from ..topology import TopologyManager, TopologyError
from ..automation import SimulatedDevice, DeviceSession, DeviceConnectionError
from ..telemetry import TelemetryCollector, TelemetryError
from ..validation import NetworkValidator, ValidationError

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure Flask application."""
    app = Flask(__name__)
    
    # Application-level state (stored on app object)
    app.topology_manager = None
    app.telemetry_collector = None
    app.validator = NetworkValidator()
    
    @app.route('/')
    def index():
        """Render main control plane interface."""
        return render_template('index.html')
    
    @app.route('/api/topology/status', methods=['GET'])
    def topology_status():
        """Get topology status."""
        if app.topology_manager is None:
            return jsonify({
                'status': 'not_created',
                'nodes': [],
                'links': []
            })
        
        nodes = list(app.topology_manager.get_all_nodes().keys())
        is_running = app.topology_manager.is_running()
        
        return jsonify({
            'status': 'running' if is_running else 'stopped',
            'nodes': nodes,
            'running': is_running
        })
    
    @app.route('/api/topology/deploy', methods=['POST'])
    def deploy_topology():
        """Deploy network topology from YAML file upload or file path."""
        yaml_path = None
        temp_file_created = False
        
        try:
            # Check if this is a file upload (multipart/form-data)
            if 'yaml_file' in request.files:
                uploaded_file = request.files['yaml_file']
                
                if uploaded_file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400
                
                # Validate file extension
                if not (uploaded_file.filename.endswith('.yaml') or uploaded_file.filename.endswith('.yml')):
                    return jsonify({'error': 'Invalid file type. Please upload a YAML file (.yaml or .yml)'}), 400
                
                # Validate file size (max 1MB)
                uploaded_file.seek(0, os.SEEK_END)
                file_size = uploaded_file.tell()
                uploaded_file.seek(0)
                
                max_size = 1024 * 1024  # 1MB
                if file_size > max_size:
                    return jsonify({'error': f'File size ({file_size} bytes) exceeds maximum allowed size (1MB)'}), 400
                
                # Save uploaded file to temporary directory
                temp_dir = Path(tempfile.gettempdir()) / 'network-topologies'
                temp_dir.mkdir(exist_ok=True, mode=0o755)
                
                # Use secure filename to prevent directory traversal
                safe_filename = secure_filename(uploaded_file.filename)
                yaml_path = temp_dir / safe_filename
                
                # Save file
                uploaded_file.save(str(yaml_path))
                temp_file_created = True
                
                logger.info(f"Received uploaded YAML file: {uploaded_file.filename} ({file_size} bytes)")
                logger.info(f"Saved to temporary location: {yaml_path}")
            
            # Fallback to file path (for backward compatibility with JSON requests)
            elif request.is_json:
                data = request.get_json()
                yaml_file = data.get('yaml_file')
                
                if not yaml_file:
                    logger.error("Deploy request missing yaml_file")
                    return jsonify({'error': 'yaml_file required'}), 400
                
                # Resolve YAML file path relative to project root
                project_root = Path(__file__).parent.parent.parent
                yaml_path = project_root / yaml_file
                
                logger.info(f"Deploying topology from file path: {yaml_path}")
                
                if not yaml_path.exists():
                    error_msg = f"YAML file not found: {yaml_file} (resolved to: {yaml_path})"
                    logger.error(error_msg)
                    return jsonify({'error': error_msg}), 400
            else:
                return jsonify({'error': 'No file uploaded and no file path provided'}), 400
            
            if not yaml_path or not yaml_path.exists():
                return jsonify({'error': 'YAML file not found'}), 400
            
            # Start Open vSwitch if needed (for Docker/Linux environments)
            import subprocess
            import time
            try:
                # Check if OVS is running
                subprocess.run(['ovs-vsctl', 'show'], 
                             capture_output=True, check=True, timeout=2)
                logger.debug("Open vSwitch is already running")
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                # OVS not running, try to start it
                try:
                    logger.info("Starting Open vSwitch...")
                    os.makedirs('/var/run/openvswitch', exist_ok=True)
                    os.makedirs('/var/log/openvswitch', exist_ok=True)
                    
                    subprocess.Popen(['ovsdb-server', '--detach', 
                                    '--pidfile=/var/run/openvswitch/ovsdb-server.pid',
                                    '--remote=punix:/var/run/openvswitch/db.sock',
                                    '--log-file=/var/log/openvswitch/ovsdb-server.log'],
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    time.sleep(2)  # Wait for database server to start
                    
                    subprocess.Popen(['ovs-vswitchd', '--detach',
                                    '--pidfile=/var/run/openvswitch/ovs-vswitchd.pid',
                                    '--log-file=/var/log/openvswitch/ovs-vswitchd.log'],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                    time.sleep(2)  # Wait for daemon to start
                    
                    # Verify OVS started successfully
                    subprocess.run(['ovs-vsctl', 'show'], 
                                 capture_output=True, check=True, timeout=5)
                    logger.info("Open vSwitch started successfully")
                except Exception as e:
                    logger.warning(f"Failed to start Open vSwitch: {e}. Deployment may still work.")
            
            # Parse desired state
            logger.info("Parsing desired state")
            parser = DesiredStateParser()
            desired_state = parser.load(str(yaml_path))
            topology_config = parser.get_topology()
            devices_config = parser.get_devices()
            
            logger.info(f"Creating topology with {len(topology_config.get('nodes', []))} nodes")
            
            # Clean up existing topology if present
            if app.topology_manager is not None:
                logger.info("Cleaning up existing topology")
                try:
                    app.topology_manager.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up existing topology: {e}")
            
            # Clean up any leftover Mininet interfaces
            try:
                import subprocess
                subprocess.run(['mn', '-c'], capture_output=True, timeout=10, check=False)
                logger.info("Cleaned up Mininet resources")
            except Exception as e:
                logger.warning(f"Error running Mininet cleanup: {e}")
            
            # Create topology
            app.topology_manager = TopologyManager()
            app.topology_manager.create_topology(topology_config)
            app.topology_manager.start()
            
            logger.info("Topology started successfully")
            
            # Initialize telemetry collector
            app.telemetry_collector = TelemetryCollector(app.topology_manager)
            
            # Render and deploy configurations
            logger.info("Rendering configurations")
            renderer = ConfigRenderer()
            rendered_configs = renderer.render_all(devices_config, topology_config)
            
            logger.info(f"Deploying configurations to {len(devices_config)} devices")
            device_instances = {}
            for device_name, device_config in devices_config.items():
                node = app.topology_manager.get_node(device_name)
                device = SimulatedDevice(
                    device_name=device_name,
                    device_type=device_config.get('type', 'switch'),
                    node=node
                )
                device_instances[device_name] = device
                
                with DeviceSession(device) as session:
                    config = rendered_configs[device_name]
                    session.deploy_config(config)
                logger.info(f"Deployed configuration to device: {device_name}")
            
            # Post-deployment: Enable IP forwarding on routers (hosts acting as routers)
            # Hosts with multiple interfaces and routes should forward packets
            for device_name, device_config in devices_config.items():
                node = app.topology_manager.get_node(device_name)
                interfaces = device_config.get('interfaces', [])
                routes = device_config.get('routes', [])
                # If device has multiple interfaces and routes, enable IP forwarding
                if len(interfaces) > 1 and len(routes) > 0:
                    node.cmd('sysctl -w net.ipv4.ip_forward=1 > /dev/null 2>&1')
                    logger.info(f"Enabled IP forwarding on router {device_name}")
            
            logger.info(f"Successfully deployed topology with {len(device_instances)} devices")
            
            # Clean up temporary file if it was created from upload
            if temp_file_created and yaml_path and yaml_path.exists():
                try:
                    yaml_path.unlink()
                    logger.debug(f"Cleaned up temporary file: {yaml_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file {yaml_path}: {e}")
            
            return jsonify({
                'status': 'success',
                'message': f'Deployed topology with {len(device_instances)} devices'
            })
            
        except (DesiredStateError, ConfigRenderingError, TopologyError,
                DeviceConnectionError) as e:
            logger.exception(f"Error deploying topology: {e}")
            # Clean up temporary file on error
            if temp_file_created and yaml_path and yaml_path.exists():
                try:
                    yaml_path.unlink()
                except Exception:
                    pass
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.exception(f"Unexpected error deploying topology: {e}")
            # Clean up temporary file on error
            if temp_file_created and yaml_path and yaml_path.exists():
                try:
                    yaml_path.unlink()
                except Exception:
                    pass
            return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
    
    @app.route('/api/telemetry/collect', methods=['POST'])
    def collect_telemetry():
        """Collect telemetry metrics."""
        if app.telemetry_collector is None:
            return jsonify({'error': 'Topology not deployed'}), 400
        
        data = request.get_json()
        source = data.get('source')
        destination = data.get('destination')
        
        if not source or not destination:
            return jsonify({'error': 'source and destination required'}), 400
        
        try:
            metrics = app.telemetry_collector.collect_all(source, destination)
            
            # Serialize metrics
            result = {}
            if metrics.latency:
                result['latency'] = {
                    'avg_ms': metrics.latency.avg_latency_ms,
                    'min_ms': metrics.latency.min_latency_ms,
                    'max_ms': metrics.latency.max_latency_ms,
                    'packet_loss_percent': metrics.latency.packet_loss_percent
                }
            
            if metrics.path:
                result['path'] = {
                    'total_hops': metrics.path.total_hops,
                    'hops': [
                        {
                            'hop_number': hop.hop_number,
                            'hostname': hop.hostname,
                            'ip_address': hop.ip_address,
                            'latency_ms': hop.latency_ms
                        }
                        for hop in metrics.path.hops
                    ]
                }
            
            return jsonify(result)
            
        except TelemetryError as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/validation/validate', methods=['POST'])
    def validate_network():
        """Validate network behavior."""
        if app.telemetry_collector is None:
            return jsonify({'error': 'Topology not deployed'}), 400
        
        data = request.get_json()
        source = data.get('source')
        destination = data.get('destination')
        
        if not source or not destination:
            return jsonify({'error': 'source and destination required'}), 400
        
        try:
            # Collect baseline and current metrics
            baseline = app.telemetry_collector.collect_all(source, destination)
            current = app.telemetry_collector.collect_all(source, destination)
            
            # Validate
            result = app.validator.validate(baseline, current)
            
            return jsonify({
                'status': result.status.value,
                'message': result.message,
                'details': result.details
            })
            
        except (TelemetryError, ValidationError) as e:
            return jsonify({'error': str(e)}), 400
    
    return app

