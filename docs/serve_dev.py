from livereload import Server, shell

if __name__ == '__main__':
    server = Server()
    server.watch('*.rst', shell('make.bat html'), delay=1)
    server.watch('*.md', shell('make.bat html'), delay=1)
    server.watch('*.py', shell('make.bat html'), delay=1)
    server.watch('_static/*', shell('make.bat html'), delay=1)
    server.watch('contributing/*', shell('make.bat html'), delay=1)
    server.serve(root='_build/html')
