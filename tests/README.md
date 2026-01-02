# Tests

Test files and scripts for NetworkControlPlane.

## Test Files

- **test_final.py** - Final integration tests
- **test_telemetry.py** - Telemetry collection tests
- **test_all_features.sh** - Test all features script
- **test-docker.sh** - Docker-specific tests
- **check_status.py** - Network status checking utility

## Running Tests

```bash
# Run all tests
./tests/test_all_features.sh

# Run Docker tests
./tests/test-docker.sh

# Run specific test
python tests/test_telemetry.py
```

## Note

These are integration and utility test files. For unit tests, see the test files within each module.

