import sys
import os
import subprocess

def main():
    if len(sys.argv) != 3:
        print('Needs configuration name and repeat runs')
        sys.exit(1)
    
    config_name = sys.argv[1]
    repeat_runs = int(sys.argv[2])
    print('Configuration name:', config_name)
    print('Repeat experiment', repeat_runs, 'times')

    os.environ['LEBENCH_DIR'] = os.path.abspath(os.path.dirname(__file__)) + '/'
    print('LEBENCH_DIR set to', os.environ['LEBENCH_DIR'])

    os.system('cd TEST_DIR/ && make')

    for i in range(repeat_runs):
        version_str = config_name + '-' + str(i)
        command_str = [os.environ['LEBENCH_DIR'] + '/TEST_DIR/OS_Eval', '0', version_str]
        print(command_str)
        subprocess.run(command_str)

        output_file = os.environ['LEBENCH_DIR'] + 'output.' + version_str + '.csv'
        output_file_dst = os.environ['LEBENCH_DIR'] + 'results/' + 'output.' + version_str + '.csv'
        os.rename(output_file, output_file_dst)
        os.remove(os.environ['LEBENCH_DIR'] + 'test_file.txt')
main()
