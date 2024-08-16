# Raspberry Pi BME280 Temperature Sensor Configuration

{ config, lib, pkgs, ... }:
{
    environment.systemPackages = [
        (pkgs.python3.withPackages (p: [
            (p.callPackage ./bme280 {})
        ]))
    ];

    hardware.i2c.enable = true;
}