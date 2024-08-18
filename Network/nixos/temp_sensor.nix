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
      description = "Temperature Sensor";
      serviceConfig.ExecStart = let
        coolBmeEnabledPython3 = (pkgs.python3.withPackages (p: [
            (p.callPackage ./bme280 {})
        ]));
      in "${coolBmeEnabledPython3}/bin/python3 ${./../../Temp_Sensor/temp_sensor.py}";
      serviceConfig.Environment = "PYTHONUNBUFFERED=1";
      wantedBy = [ "multi-user.target" ];
  };

    systemd.services.temp-sensor-server = {
      description = "Temperature Sensor Sever";
      serviceConfig.ExecStart = let
        coolBmeEnabledPython3 = (pkgs.python3.withPackages (p: [
            (p.callPackage ./bme280 {})
        ]));
      in "${coolBmeEnabledPython3}/bin/python3 ${./../../Temp_Sensor/server_temperature.py}";
      serviceConfig.Environment = "PYTHONUNBUFFERED=1";
      wantedBy = [ "multi-user.target" ];
  };
}