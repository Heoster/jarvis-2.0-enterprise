"""Setup script for JARVIS Enhanced features."""

import subprocess
import sys
from pathlib import Path
import os


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")


def print_step(step, text):
    """Print step information."""
    print(f"[{step}] {text}")


def run_command(cmd, description):
    """Run command and handle errors."""
    print(f"\n▶ {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check Python version."""
    print_step(1, "Checking Python version")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False


def create_directories():
    """Create necessary directories."""
    print_step(2, "Creating directories")
    
    directories = [
        "data/students",
        "data/knowledge_graphs",
        "logs",
        "models"
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created {directory}")
    
    return True


def install_dependencies():
    """Install Python dependencies."""
    print_step(3, "Installing dependencies")
    
    # Check if requirements file exists
    req_file = Path("requirements-enhanced.txt")
    if not req_file.exists():
        print("❌ requirements-enhanced.txt not found")
        return False
    
    # Install requirements
    success = run_command(
        f"{sys.executable} -m pip install -r requirements-enhanced.txt",
        "Installing Python packages"
    )
    
    return success


def download_spacy_model():
    """Download spaCy language model."""
    print_step(4, "Downloading spaCy model")
    
    success = run_command(
        f"{sys.executable} -m spacy download en_core_web_sm",
        "Downloading en_core_web_sm"
    )
    
    return success


def verify_installation():
    """Verify all components are installed."""
    print_step(5, "Verifying installation")
    
    components = {
        'spacy': 'spaCy',
        'sentence_transformers': 'Sentence Transformers',
        'transformers': 'Transformers',
        'langchain': 'LangChain',
        'networkx': 'NetworkX',
        'jinja2': 'Jinja2',
        'sklearn': 'scikit-learn'
    }
    
    all_installed = True
    
    for module, name in components.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} not found")
            all_installed = False
    
    return all_installed


def test_components():
    """Test core components."""
    print_step(6, "Testing components")
    
    try:
        # Test intent classifier
        from core.intent_classifier_enhanced import EnhancedIntentClassifier
        classifier = EnhancedIntentClassifier()
        print("  ✅ Intent Classifier")
    except Exception as e:
        print(f"  ❌ Intent Classifier: {e}")
        return False
    
    try:
        # Test semantic matcher
        from core.semantic_matcher import SemanticMatcher
        matcher = SemanticMatcher()
        print("  ✅ Semantic Matcher")
    except Exception as e:
        print(f"  ⚠️  Semantic Matcher: {e} (will download on first use)")
    
    try:
        # Test memory
        from storage.contextual_memory_enhanced import EnhancedContextualMemory
        memory = EnhancedContextualMemory()
        print("  ✅ Enhanced Memory")
    except Exception as e:
        print(f"  ❌ Enhanced Memory: {e}")
        return False
    
    try:
        # Test knowledge graph
        from core.knowledge_graph import KnowledgeGraph
        kg = KnowledgeGraph()
        print("  ✅ Knowledge Graph")
    except Exception as e:
        print(f"  ❌ Knowledge Graph: {e}")
        return False
    
    try:
        # Test unified JARVIS
        from core.jarvis_unified import UnifiedJarvis
        jarvis = UnifiedJarvis()
        print("  ✅ Unified JARVIS")
    except Exception as e:
        print(f"  ❌ Unified JARVIS: {e}")
        return False
    
    return True


def run_tests():
    """Run test suite."""
    print_step(7, "Running tests")
    
    test_file = Path("tests/test_jarvis_enhanced.py")
    if not test_file.exists():
        print("⚠️  Test file not found, skipping tests")
        return True
    
    success = run_command(
        f"{sys.executable} -m pytest {test_file} -v --tb=short",
        "Running test suite"
    )
    
    return success


def print_summary(success):
    """Print installation summary."""
    print_header("INSTALLATION SUMMARY")
    
    if success:
        print("✅ JARVIS Enhanced installation completed successfully!\n")
        print("Next steps:")
        print("  1. Run interactive demo:")
        print("     python examples/jarvis_enhanced_demo.py --mode interactive\n")
        print("  2. Run all demos:")
        print("     python examples/jarvis_enhanced_demo.py --mode all\n")
        print("  3. Check system status:")
        print("     python examples/jarvis_enhanced_demo.py --diagnose\n")
        print("  4. Read documentation:")
        print("     - JARVIS_QUICK_REFERENCE.md")
        print("     - INTEGRATION_GUIDE.md")
        print("     - JARVIS_UPGRADES_COMPLETE.md\n")
        print("🎉 JARVIS Enhanced is ready to use! ✨🚀")
    else:
        print("❌ Installation encountered errors\n")
        print("Troubleshooting:")
        print("  1. Check Python version (3.8+ required)")
        print("  2. Ensure pip is up to date: python -m pip install --upgrade pip")
        print("  3. Try installing dependencies manually:")
        print("     pip install -r requirements-enhanced.txt")
        print("  4. Download spaCy model manually:")
        print("     python -m spacy download en_core_web_sm")
        print("  5. Check logs for detailed errors\n")


def main():
    """Main setup function."""
    print_header("JARVIS ENHANCED - SETUP")
    print("This script will install and configure JARVIS Enhanced features.\n")
    
    steps = [
        ("Python version check", check_python_version),
        ("Directory creation", create_directories),
        ("Dependency installation", install_dependencies),
        ("spaCy model download", download_spacy_model),
        ("Installation verification", verify_installation),
        ("Component testing", test_components),
    ]
    
    # Optional: Run tests
    run_tests_flag = input("Run test suite? (y/n, default: n): ").strip().lower()
    if run_tests_flag == 'y':
        steps.append(("Test suite", run_tests))
    
    print("\nStarting installation...\n")
    
    success = True
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n⚠️  {step_name} failed, but continuing...\n")
            success = False
    
    print_summary(success)
    
    return 0 if success else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
