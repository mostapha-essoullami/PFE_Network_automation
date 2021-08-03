print("\n\n *** Sample ZTP Day0 Python Script *** \n\n")

# Importing cli module
import cli


print("\n\n *** Executing show version *** \n\n")
cli_command = "show version"
ver=cli.cli(cli_command)
print(ver)

print("\n\n *** Get Serial *** \n\n")
serial=cli.cli("show version | include Processor").split()[-1].rstrip()
print(serial)

print("\n\n *** Copy config  *** \n\n")
print("getting {}.conf ".format(serial))

#command="copy tftp://192.168.255.57/{}.config running-config".format(serial)

command="copy tftp://192.168.255.57/test.config running-config".format(serial)

cli.cli(command)

print("\n\n *** ZTP Day0 Python Script Execution Complete *** \n\n")