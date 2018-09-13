import unittest

loader = unittest.TestLoader()
start_dir = '.'
suite = loader.discover(start_dir)

runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)

if __name__ == "__main__":
    unittest.main()
