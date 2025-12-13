import pytest
import time
import httpx
from testcontainers.core.container import DockerContainer
from bugspotter_intelligence.config import Settings


@pytest.fixture(scope="session")
def ollama_container():
    """
    Start Ollama container for integration tests (CPU-only mode)
    Scope: session (shared across all tests)
    """
    # Use generic DockerContainer to avoid GPU issues
    container = DockerContainer("ollama/ollama:latest")
    container.with_exposed_ports(11434)

    # Force CPU-only mode (no GPU runtime)
    container.with_env("OLLAMA_HOST", "0.0.0.0:11434")
    container.with_env("CUDA_VISIBLE_DEVICES", "")  # Disable CUDA

    container.start()

    # Get connection details
    host = container.get_container_host_ip()
    port = container.get_exposed_port(11434)
    base_url = f"http://{host}:{port}"

    # Wait for Ollama to be ready
    print(f"\nWaiting for Ollama at {base_url}...")
    for i in range(30):
        try:
            response = httpx.get(f"{base_url}/api/tags", timeout=2.0)
            if response.status_code == 200:
                print(f"✅ Ollama ready after {i + 1} seconds")
                break
        except Exception:
            time.sleep(1)
    else:
        container.stop()
        raise TimeoutError("Ollama failed to start after 30 seconds")

    # Pull small model for testing
    print("Pulling tinyllama model (2-3 minutes)...")
    exit_code, output = container.exec("ollama pull tinyllama:1.1b")

    if exit_code == 0:
        print("✅ Model pulled successfully")
    else:
        print(f"⚠️  Model pull output: {output}")

    yield {
        "host": host,
        "port": port,
        "base_url": base_url,
        "container": container
    }

    # Cleanup
    container.stop()


@pytest.fixture
def settings_with_testcontainer(ollama_container):
    """Settings configured to use testcontainer Ollama"""
    settings = Settings()
    settings.ollama_base_url = ollama_container["base_url"]
    settings.ollama_model = "tinyllama:1.1b"
    return settings