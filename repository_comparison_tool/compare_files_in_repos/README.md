# JFrog Artifactory Repository Comparison Tool

A comprehensive Python tool for comparing artifacts between source and target JFrog Artifactory instances and generating transfer commands.

## 🚀 Features

- **Multi-format Support**: Compare any repository type (local, remote, virtual, federated)
- **AQL-based Queries**: Uses Artifactory Query Language with pagination for large repositories
- **Dual Command Generation**: Generate either curl commands or JFrog CLI commands
- **JFrog Version Compatibility**: Works with both JFrog 6.x and 7.x+
- **SHA256 Verification**: Compares files using SHA256 checksums for accuracy
- **Parallel Processing**: Multi-threaded processing for improved performance
- **Repository Filtering**: Compare specific repositories from a file list
- **Comprehensive Logging**: Detailed logging with progress tracking

## 📋 Prerequisites

### Required

- Python 3.7 or higher
- `requests` library: `pip install requests`

### For curl commands (default)

- `curl` command available on system

### For JFrog CLI commands

- JFrog CLI installed: https://jfrog.com/getcli/
- JFrog CLI configured with server profiles

## ⚙️ Installation

1. **Clone or download the script**

```bash
git clone <repository-url>
cd compare_repos
```

2. **Create a Python virtual environment**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

3. **Install Python dependencies**

```bash
# Install from requirements.txt
pip install -r requirements.txt
```

4. **Verify installation**

```bash
python compare_repos.py --help
```

## 🔧 Configuration

The script requires a JSON configuration file. Create one based on your JFrog Artifactory version:

### JFrog 7.x+ Configuration (config.json)

```json
{
  "source_server": "source",
  "target_server": "target",
  "parallel_workers": 20,
  "request_timeout": 120,
  "retry_attempts": 3,
  "servers": {
    "source": {
      "url": "https://source.jfrog.io/artifactory",
      "token": "your-source-token"
    },
    "target": {
      "url": "https://target.jfrog.io/artifactory",
      "token": "your-target-token"
    }
  }
}
```

### JFrog 6.x Configuration (config_6x.json)

```json
{
  "source_server": "source",
  "target_server": "target",
  "servers": {
    "source": {
      "url": "https://source.jfrog.io",
      "token": "your-source-token"
    },
    "target": {
      "url": "https://target.jfrog.io",
      "token": "your-target-token"
    }
  }
}
```

### Authentication Options

**Option 1: Access Tokens (Recommended)**

```json
{
  "url": "https://myartifactory.jfrog.io/artifactory",
  "token": "your-access-token"
}
```

**Option 2: Username/Password**

```json
{
  "url": "https://myartifactory.jfrog.io/artifactory",
  "username": "your-username",
  "password": "your-password"
}
```

## 🚦 Usage

### Basic Usage

```bash
# Compare all local repositories
python compare_repos.py --config config.json

# Compare specific repository types
python compare_repos.py --config config.json --repo-type remote
python compare_repos.py --config config.json --repo-type virtual
```

### Repository Filtering

Create a `repos.txt` file with repository names (one per line):

```
repo1
repo2
repo3
```

Then run:

```bash
python compare_repos.py --config config.json --repos-file repos.txt
```

### Command Type Selection

**Generate curl commands (default):**

```bash
python compare_repos.py --config config.json --command-type curl
```

**Generate JFrog CLI commands:**

```bash
python compare_repos.py --config config.json --command-type jfrog
```

## 📝 Command Line Arguments

| Argument         | Short | Required | Description                                              |
| ---------------- | ----- | -------- | -------------------------------------------------------- |
| `--config`       | `-c`  | ✅       | Path to JSON configuration file                          |
| `--repos-file`   | `-r`  | ❌       | Text file with repository names to compare               |
| `--repo-type`    |       | ❌       | Type of repositories (local, remote, virtual, federated) |
| `--command-type` |       | ❌       | Command type to generate (curl, jfrog)                   |

## 📁 Output Structure

The script creates a timestamped output directory:

```
out_<timestamp>/
├── summary.txt           # Overall comparison summary
├── fulllist.log         # All different files across repositories
├── compare_repos.log    # Detailed execution log
└── <repo-name>/
    ├── <repo-name>.txt  # Files different in this repository
    └── transfer.txt     # Transfer commands for this repository
```

## 🔄 Command Types Comparison

### CURL Commands

```bash
# Download
curl -f -s -L -o "file.jar" "https://source.jfrog.io/artifactory/repo/path/file.jar"
# Upload
curl -f -s -X PUT -T "file.jar" "https://target.jfrog.io/artifactory/repo/path/file.jar"
# Cleanup
rm -f "file.jar"
```

**Benefits:**

- ✅ No additional tools required
- ✅ Direct HTTP control
- ✅ Works anywhere curl is available

### JFrog CLI Commands

```bash
# Download
jf rt download --server-id=source "repo/path/file.jar" "file.jar"
# Upload
jf rt upload --server-id=target "file.jar" "repo/path/file.jar"
```

**Benefits:**

- ✅ Better integration with JFrog ecosystem
- ✅ Automatic authentication handling
- ✅ No manual cleanup required
- ✅ Better error handling and retry logic

## 🚀 JFrog CLI Setup (for JFrog CLI commands)

```bash
# Configure source server
jf config add source --url=https://source.jfrog.io --access-token=your-source-token

# Configure target server
jf config add target --url=https://target.jfrog.io --access-token=your-target-token

# Verify configuration
jf config show
```

## ⚡ Performance & Scalability

### AQL with Pagination

The script uses Artifactory Query Language (AQL) with pagination to handle large repositories efficiently:

- **Batch Processing**: Processes files in batches of 100,000
- **Memory Efficient**: Avoids loading millions of files into memory
- **Progress Tracking**: Shows real-time progress percentages
- **No Timeouts**: Each batch completes quickly

### Example AQL Query

```javascript
items
  .find({ repo: "my-repo" })
  .include("name", "path", "sha256")
  .offset(0)
  .limit(100000);
```

## 🐛 Troubleshooting

### Common Issues

**Config file not found:**

```
Error: Configuration file is required and must exist: config.json
```

- Ensure the config file path is correct
- Check file permissions

**Authentication failed:**

```
Failed to fetch repositories: 401 Unauthorized
```

- Verify your access token or username/password
- Check token permissions and expiration

**Large repository timeouts:**

- The script uses AQL with pagination to avoid timeouts
- Adjust `request_timeout` in config for slower networks

**JFrog CLI commands not working:**

- Ensure JFrog CLI is installed: `jf --version`
- Configure server profiles: `jf config add <server-id>`
- Verify server IDs match config file

### Debugging

Enable debug logging by adding to config:

```json
{
  "log_level": "DEBUG"
}
```

## 📊 Performance Tips

1. **Adjust Workers**: Tune `parallel_workers` (default: 20) based on your system
2. **Repository Filtering**: Use `--repos-file` to compare only needed repositories
3. **Network Optimization**: Increase `request_timeout` for slow networks
4. **Batch Size**: AQL pagination uses 100K files per batch (configurable in code)
