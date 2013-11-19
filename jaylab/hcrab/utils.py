#coding=utf-8
import subprocess
def disk_usage():
    df = subprocess.Popen(["df", "-lh"], stdout=subprocess.PIPE)
    output = df.communicate()[0]
    return output.split("\n")[1].split()

if __name__ == '__main__':
    print disk_usage()
