#!/usr/bin/env python3
"""
Package Strands Agent Lambda function for deployment
This script creates the necessary ZIP files for the Lambda function and its dependencies.
"""

import os
import shutil
import subprocess
import zipfile
from pathlib import Path
import sys


def create_lambda_package():
    """Create packages for Lambda deployment following AWS best practices."""
    current_dir = Path.cwd()
    packaging_dir = current_dir / "packaging"
    
    # Paths for the Lambda application
    app_dir = current_dir / "lambda" / "strands-agent"
    app_deployment_zip = packaging_dir / "app.zip"
    
    # Paths for dependencies
    dependencies_dir = packaging_dir / "_dependencies"
    dependencies_deployment_zip = packaging_dir / "dependencies.zip"
    requirements_file = app_dir / "requirements.txt"
    
    print("🚀 Starting Lambda packaging process...")
    
    # Create packaging directory if it doesn't exist
    packaging_dir.mkdir(exist_ok=True)
    
    # Clean up previous builds
    if dependencies_dir.exists():
        shutil.rmtree(dependencies_dir)
    if app_deployment_zip.exists():
        app_deployment_zip.unlink()
    if dependencies_deployment_zip.exists():
        dependencies_deployment_zip.unlink()
    
    print("📦 Installing Python dependencies for ARM64 architecture...")
    
    # Create dependencies directory
    dependencies_dir.mkdir(exist_ok=True)
    
    # Install Python dependencies for Lambda ARM64 architecture
    if requirements_file.exists():
        pip_command = [
            sys.executable, "-m", "pip", "install",
            "-r", str(requirements_file),
            "--python-version", "3.12",
            "--platform", "manylinux2014_aarch64",
            "--target", str(dependencies_dir),
            "--only-binary=:all:",
            "--no-deps"  # First pass without dependencies
        ]
        
        try:
            result = subprocess.run(pip_command, check=True, capture_output=True, text=True)
            print("✅ Base packages installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Base package installation had issues: {e}")
            print("Stderr:", e.stderr)
        
        # Second pass to get all dependencies
        pip_command_with_deps = [
            sys.executable, "-m", "pip", "install",
            "-r", str(requirements_file),
            "--python-version", "3.12", 
            "--platform", "manylinux2014_aarch64",
            "--target", str(dependencies_dir),
            "--only-binary=:all:"
        ]
        
        try:
            result = subprocess.run(pip_command_with_deps, check=True, capture_output=True, text=True)
            print("✅ All dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Dependency installation had issues: {e}")
            print("Stderr:", e.stderr)
            # Continue anyway as some packages might still work
    else:
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    print("📁 Creating dependencies ZIP file...")
    
    # Create dependencies ZIP file with proper Lambda layer structure
    with zipfile.ZipFile(dependencies_deployment_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(dependencies_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Lambda layers expect files in /opt/python/ structure
                arcname = Path("python") / os.path.relpath(file_path, dependencies_dir)
                zipf.write(file_path, arcname)
    
    print("📁 Creating application ZIP file...")
    
    # Create application ZIP file
    with zipfile.ZipFile(app_deployment_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(app_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Skip requirements.txt and other non-Python files if desired
                if file.endswith(('.py', '.json', '.txt')):
                    arcname = os.path.relpath(file_path, app_dir)
                    zipf.write(file_path, arcname)
    
    # Print package information
    app_size = app_deployment_zip.stat().st_size / (1024 * 1024)  # MB
    deps_size = dependencies_deployment_zip.stat().st_size / (1024 * 1024)  # MB
    
    print(f"✅ Packaging complete!")
    print(f"📊 Application package: {app_deployment_zip} ({app_size:.2f} MB)")
    print(f"📊 Dependencies package: {dependencies_deployment_zip} ({deps_size:.2f} MB)")
    
    return True


def main():
    """Main function to run the packaging process."""
    print("🔧 Strands Agent Lambda Packaging Tool")
    print("=" * 50)
    
    try:
        success = create_lambda_package()
        if success:
            print("\n🎉 Packaging completed successfully!")
            print("You can now run 'npx cdk deploy StrandsAgentLambdaStack' to deploy the Lambda function.")
        else:
            print("\n❌ Packaging failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 An error occurred during packaging: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
