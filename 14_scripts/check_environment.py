"""
Environment Check Script - Run before first backend startup
Checks all dependencies, configurations, and services
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import subprocess
import socket
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("="*70)
print("🔍 Financial Agent Environment Check")
print("="*70)
print()

# Track check results
checks_passed = 0
checks_failed = 0
warnings = []

def check_pass(name):
    global checks_passed
    print(f"✅ {name}")
    checks_passed += 1

def check_fail(name, reason=""):
    global checks_failed
    print(f"❌ {name}")
    if reason:
        print(f"   Reason: {reason}")
    checks_failed += 1

def check_warn(name, reason=""):
    print(f"⚠️  {name}")
    if reason:
        print(f"   Note: {reason}")
    warnings.append(f"{name}: {reason}")

# ==================== 1. Python Version Check ====================
print("1️⃣  Checking Python version...")
python_version = sys.version_info
if python_version.major == 3 and python_version.minor >= 10:
    check_pass(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
else:
    check_fail(f"Python {python_version.major}.{python_version.minor}", "Requires Python 3.10+")

print()

# ==================== 2. Required Packages Check ====================
print("2️⃣  Checking required packages...")

required_packages = [
    ("fastapi", "FastAPI framework"),
    ("uvicorn", "ASGI server"),
    ("openai", "OpenAI SDK for cloud LLM"),
    ("pymilvus", "Milvus vector database client"),
    ("pymysql", "MySQL database connector"),
    ("torch", "PyTorch for embeddings"),
    ("transformers", "HuggingFace transformers"),
    ("dashscope", "Alibaba DashScope SDK (optional)"),
    ("loguru", "Logging utility"),
    ("python-dotenv", "Environment variable management"),
]

for package, description in required_packages:
    try:
        __import__(package.replace("-", "_"))
        check_pass(f"{package} ({description})")
    except ImportError:
        if package == "dashscope":
            check_warn(package, "Optional - not needed if using OpenAI compatible mode")
        else:
            check_fail(package, f"Install with: pip install {package}")

print()

# ==================== 3. Environment Variables Check ====================
print("3️⃣  Checking environment variables...")

env_checks = [
    ("OPENAI_COMPATIBLE_BASE_URL", "OpenAI compatible API base URL", True),
    ("OPENAI_COMPATIBLE_API_KEY", "OpenAI compatible API key", True),
    ("LLM_TEMPERATURE", "LLM temperature setting", False),
    ("DEFAULT_LLM_MODEL", "Default LLM model", False),
    ("DB_HOST", "Database host", True),
    ("DB_PORT", "Database port", True),
    ("DB_USER", "Database user", True),
    ("DB_PASSWORD", "Database password", True),
    ("MILVUS_URI", "Milvus vector database URI", True),
]

for env_var, description, required in env_checks:
    value = os.getenv(env_var)
    if value:
        if env_var == "OPENAI_COMPATIBLE_API_KEY" or env_var == "DB_PASSWORD":
            masked_value = value[:10] + "..." if len(value) > 10 else "***"
            check_pass(f"{env_var} = {masked_value}")
        else:
            check_pass(f"{env_var} = {value}")
    else:
        if required:
            check_fail(env_var, f"Required but not set. Please add to .env file")
        else:
            check_warn(env_var, f"Not set, will use default value")

print()

# ==================== 4. Database Connection Check ====================
print("4️⃣  Checking database connections...")

# MySQL check
try:
    import pymysql
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "3306"))
    db_user = os.getenv("DB_USER", "root")
    db_password = os.getenv("DB_PASSWORD", "")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((db_host, db_port))
    sock.close()

    if result == 0:
        check_pass(f"MySQL connection ({db_host}:{db_port})")
    else:
        check_fail(f"MySQL connection ({db_host}:{db_port})", "Cannot connect to MySQL server")
        print("   💡 Start MySQL or update DB_HOST/DB_PORT in .env")
except Exception as e:
    check_fail("MySQL connection", str(e))

# Milvus check
try:
    milvus_uri = os.getenv("MILVUS_URI", "http://localhost:19530")
    # Extract host and port from URI
    if "://" in milvus_uri:
        milvus_host = milvus_uri.split("://")[1].split(":")[0]
        milvus_port = int(milvus_uri.split(":")[2]) if ":" in milvus_uri.split("://")[1] else 19530
    else:
        milvus_host = "localhost"
        milvus_port = 19530

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((milvus_host, milvus_port))
    sock.close()

    if result == 0:
        check_pass(f"Milvus connection ({milvus_host}:{milvus_port})")
    else:
        check_fail(f"Milvus connection ({milvus_host}:{milvus_port})", "Cannot connect to Milvus server")
        print("   💡 Start Milvus with:")
        print("      docker run -d --name milvus-standalone -p 19530:19530 milvusdb/milvus:latest milvus run standalone")
except Exception as e:
    check_fail("Milvus connection", str(e))

print()

# ==================== 5. Directory Structure Check ====================
print("5️⃣  Checking directory structure...")

required_dirs = [
    "01_backend",
    "02_frontend",
    "03_agent",
    "09_retrieve",
    "10_storage",
    "11_report/output",
]

for dir_path in required_dirs:
    full_path = project_root / dir_path
    if full_path.exists():
        check_pass(f"Directory: {dir_path}")
    else:
        check_warn(f"Directory: {dir_path}", "Will be created automatically if needed")
        full_path.mkdir(parents=True, exist_ok=True)

print()

# ==================== 6. LLM Configuration Check ====================
print("6️⃣  Checking LLM configuration...")

llm_model = os.getenv("DEFAULT_LLM_MODEL", "qwen3.6-plus")
llm_temp = os.getenv("LLM_TEMPERATURE", "0.1")

check_pass(f"LLM Model: {llm_model}")
check_pass(f"LLM Temperature: {llm_temp}")

# Check if model name is valid for cloud mode
cloud_indicators = ['qwen-plus', 'qwen-turbo', 'qwen-max', 'qwen-long', 'qwen2.5', 'qwen3']
is_cloud_model = any(indicator in llm_model.lower() for indicator in cloud_indicators) and '/' not in llm_model

if is_cloud_model:
    check_pass(f"Model type: Cloud (OpenAI compatible mode)")
else:
    check_warn(f"Model type: Local", "Make sure local model files exist")

print()

# ==================== Summary ====================
print("="*70)
print("📊 Check Summary")
print("="*70)
print(f"✅ Passed: {checks_passed}")
print(f"❌ Failed: {checks_failed}")
print(f"⚠️  Warnings: {len(warnings)}")
print()

if warnings:
    print("Warnings:")
    for warning in warnings:
        print(f"  ⚠️  {warning}")
    print()

if checks_failed == 0:
    print("🎉 All critical checks passed! You can start the backend.")
    print()
    print("To start the backend:")
    print("  cd 01_backend")
    print("  python main.py")
    print()
    print("Then access API docs at: http://localhost:8000/docs")
    sys.exit(0)
else:
    print("❌ Some critical checks failed. Please fix the issues above before starting.")
    print()
    print("Common fixes:")
    print("  1. Install missing packages: pip install -r requirements.txt")
    print("  2. Configure .env file with correct API keys and database settings")
    print("  3. Start required services (MySQL, Milvus)")
    sys.exit(1)