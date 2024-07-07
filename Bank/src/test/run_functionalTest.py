import subprocess
import os
import sys
import time
# 将项目根目录添加到 PYTHONPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(project_root)
# 确定脚本的路径
backend_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/backend/main.py'))
# Copy the following test you want to run
#   functionalTestATM.py
#   functionalTestApp.py
#   functionalTestMultipleUser.py
test_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'functionalTestMultipleUser.py'))

def run_backend():
    # 启动 backend 脚本
    backend_process = subprocess.Popen(['python', backend_script])
    return backend_process

def run_tests():
    # 启动 functionalTest 脚本
    test_process = subprocess.Popen(['python', test_script])
    return test_process

if __name__ == "__main__":
    backend_process = run_backend()
    # 等待 backend 启动
    time.sleep(3)  # 你可以调整等待时间

    test_process = run_tests()

    # 等待测试完成
    test_process.wait()
    # 完成后终止 backend 进程
    backend_process.terminate()
    backend_process.wait()