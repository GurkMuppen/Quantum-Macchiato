import subprocess

with open("test.out", "w") as outfile:
    process = subprocess.Popen(
        ["conda", "run", "-n", "qespresso", "pw.x", "-in", "test.in"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    for line in process.stdout:
        outfile.write(line)
        outfile.flush()
    process.wait()

print("Hello World!")


