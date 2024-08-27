# Start FPGA's Mic Server on Boot

# command to run on boot
# sudo server -r -g 255

{ config, lib, pkgs, ... }:
{

    systemd.services.start-mic-server = {
      description = "Start Mic Server";

      wantedBy = [ "multi-user.target" ];
      after = ["network-online.target" "bitstream.service" ];

      serviceConfig = {
          Environment = "PYTHONUNBUFFERED=1";
          ExecStart = "${pkgs.design.application}/bin/server -r -g 255";
          User = "root";
          Group = "root";
      };
    };
}