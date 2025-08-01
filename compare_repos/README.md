# JFrog Artifactory Repository Comparison Tool

This Python-based tool compares artifacts between source and target JFrog Artifactory instances and generates curl-based transfer commands.

## Features

- **Pure Python Implementation**: No dependency on JFrog CLI
- **Curl-based Commands**: Generates standard curl commands for maximum compatibility
- **Parallel Processing**: Configurable parallel workers for efficient comparison
- **Comprehensive Logging**: Detailed logging with configurable levels
- **Configuration File Support**: JSON-based configuration for easy management
- **Auto-generated File Filtering**: Intelligent filtering of Artifactory-generated files
- **Transfer Command Generation**: Ready-to-execute curl commands for file transfers
- **Progress Tracking**: Real-time progress monitoring and reporting
- **Resume Capability**: Ability to retry failed transfers

## Prerequisites

- Python 3.7 or higher
- Required Python packages (install via requirements.txt)

```bash
pip install -r requirements.txt
```

## Configuration

### Method 1: Configuration File (Recommended)

Create a `config.json` file with your Artifactory settings:

```json
{
  "source_server": "source-artifactory",
  "target_server": "target-artifactory",
  "servers": {
    "source-artifactory": {
      "url": "https://your-source-artifactory.jfrog.io",
      "token": "your-source-token-here",
      "username": "",
      "password": ""
    },
    "target-artifactory": {
      "url": "https://your-target-artifactory.jfrog.io",
      "token": "your-target-token-here",
      "username": "",
      "password": ""
    }
  },
  "parallel_workers": 20,
  "request_timeout": 30,
  "retry_attempts": 3,
  "log_level": "INFO"
}
```

### Method 2: Environment Variables

The tool supports multiple environment variable naming patterns for maximum flexibility:

#### Option 1: Generic Names (Recommended)

```bash
# Token-based authentication (Recommended)
export SOURCE_ARTIFACTORY_TOKEN="your-source-token"
export TARGET_ARTIFACTORY_TOKEN="your-target-token"

# OR Username/password authentication
export SOURCE_ARTIFACTORY_USER="your-source-username"
export SOURCE_ARTIFACTORY_PASS="your-source-password"
export TARGET_ARTIFACTORY_USER="your-target-username"
export TARGET_ARTIFACTORY_PASS="your-target-password"
```

## Usage

## Generate commands to transfer files

### Basic Usage with Configuration File

```bash
python compare_repos.py --config config.json
```

### Usage with Repository Filter

To compare only specific repositories, create a text file with repository names (one per line):

```bash
# Create a repository list file
cat > my_repos.txt << EOF
maven-local
npm-local
docker-local
# Comments are supported
pypi-local
EOF

# Run comparison for only these repositories
python compare_repos.py --config config.json --repos-file my_repos.txt
```

### Complete Example

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure authentication
export SOURCE_ARTIFACTORY_TOKEN="your-source-token"
export TARGET_ARTIFACTORY_TOKEN="your-target-token"

# 3. Run comparison
python compare_repos.py --source-server mycompany-source --target-server mycompany-target

# 4. Review results
ls out_*/
cat out_*/summary.txt

# 5. Execute transfers (optional)
python transfer_files.py --output-dir out_1234567890
```

## Output Structure

The tool generates a timestamped output directory with the following structure:

```
out_1234567890/
├── compare_repos.log          # Detailed execution log
├── summary.txt               # Summary report
├── fulllist.log             # Complete list of differing files
├── repo1/
│   ├── repo1.txt           # List of files to transfer for repo1
│   └── transfer.txt        # Curl commands for repo1
├── repo2/
│   ├── repo2.txt           # List of files to transfer for repo2
│   └── transfer.txt        # Curl commands for repo2
└── ...
```

### File Descriptions

- **`summary.txt`**: Overall summary with statistics and usage instructions
- **`fulllist.log`**: Complete numbered list of all differing files across all repositories
- **`<repo>.txt`**: Repository-specific list of files that need to be transferred
- **`transfer.txt`**: Ready-to-execute curl commands for transferring files
- **`compare_repos.log`**: Detailed execution log with debugging information

## Transfer Commands

The generated `transfer.txt` files contain curl commands in the format:

```bash
curl -f -s -L -H "Authorization: Bearer token" -o "file.jar" "https://source.jfrog.io/artifactory/repo/path/file.jar" && curl -f -s -X PUT -H "Authorization: Bearer token" -T "file.jar" "https://target.jfrog.io/artifactory/repo/path/file.jar" && rm -f "file.jar"
```

### Executing Transfer Commands

#### Using the transfer script (recommended):

```bash
python transfer_files.py --output-dir out_1234567890 --parallel-workers 10
```

## Transfer Management

Use the included `transfer_files.py` script for managed file transfers:

### Features of transfer_files.py:

- **Parallel execution** with configurable workers
- **Progress tracking** and logging
- **Error handling** and retry capability
- **Failed transfer logging** for manual review
- **Detailed reporting** with statistics

### Transfer Script Usage:

```bash
# Transfer all files with progress tracking
python transfer_files.py --output-dir out_1234567890

# Use custom number of parallel workers
python transfer_files.py --output-dir out_1234567890 --parallel-workers 5

# Transfer specific repository only
python transfer_files.py --transfer-file out_1234567890/repo1/transfer.txt

# Dry run to validate commands
python transfer_files.py --output-dir out_1234567890 --dry-run
```

## Configuration Options

| Option             | Description                                  | Default |
| ------------------ | -------------------------------------------- | ------- |
| `parallel_workers` | Number of concurrent repository comparisons  | 20      |
| `request_timeout`  | HTTP request timeout in seconds              | 30      |
| `retry_attempts`   | Number of retry attempts for failed requests | 3       |
| `log_level`        | Logging level (DEBUG, INFO, WARNING, ERROR)  | INFO    |

## Authentication Methods

The tool supports multiple authentication methods:

1. **Bearer Token** (Recommended): Use API tokens for secure authentication
2. **Basic Authentication**: Username and password combination
3. **Environment Variables**: Set credentials via environment variables

### Priority Order:

1. Token (if provided) - takes precedence over username/password
2. Username/Password (if both provided)
3. Environment variables (fallback if no config file authentication)

## File Filtering

The tool automatically filters out Artifactory-generated files:

### Skipped Files:

- `repository.catalog`
- `maven-metadata.xml`
- `Packages.bz2`, `Packages.gz`, `Packages`
- `Release`, `repomd.xml*`
- Various repository-specific metadata files

### Skipped Patterns:

- Paths starting with `.npm`, `.jfrog`, `.pypi`, `.composer`
- Files matching `index.yaml`, `versions`
- Upload temporary files (`_uploads`)
