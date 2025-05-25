def test_config_file_exists(host):
    config_file = host.file("/etc/alloy/config.alloy")
    assert config_file.exists
    assert config_file.is_file
    assert config_file.user == "root"
    assert config_file.group == "root"
    assert config_file.mode == 0o600
