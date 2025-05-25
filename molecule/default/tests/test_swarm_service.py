def test_alloy_service_running(host):
    cmd = host.run(
        "docker service ls --filter name=alloy --format '{{.Name}} {{.Replicas}}'"
    )
    assert cmd.rc == 0
    assert "alloy" in cmd.stdout
    assert "1/1" in cmd.stdout


def test_alloy_service_is_listening(host):
    assert host.socket("tcp://0.0.0.0:12345").is_listening
