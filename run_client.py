import sys
import os


root_dir = os.path.dirname(os.path.abspath(__file__))


src_path = os.path.join(root_dir, 'src')
sys.path.insert(0, src_path)

try:
    from client.ClientUI import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Import Error: {e}")