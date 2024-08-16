# Raspberry Pi BME280 Temperature Sensor Configuration

{ config, lib, pkgs, ... }:
{
    environment.systemPackages = [
        (pkgs.python3.withPackages (p: [
            (p.callPackage ./bme280 {})
        ]))
    ];

    hardware.i2c.enable = true;



  systemd.services.temp-sensor = {
      description = "Custom NAT setup for wlp1s0u1u4";
      after = [ "network.target" ];
      serviceConfig.ExecStart = let
        coolBmeEnabledPython3 = (pkgs.python3.withPackages (p: [
            (p.callPackage ./bme280 {})
        ]));
      in "${coolBmeEnabledPython3}/bin/python3 ${./../../Temp_Sensor/temp_sensor_server.py}";
      serviceConfig.Environment = "PYTHONUNBUFFERED=1";
      wantedBy = [ "multi-user.target" ];
  };
}