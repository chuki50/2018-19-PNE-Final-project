import http.server
import socketserver
import termcolor
import requests

socketserver.TCPServer.allow_reuse_address = True

PORT = 8000


class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        # Print the request line
        print("GET received! Request line:")
        termcolor.cprint("  " + self.requestline, 'cyan')
        print("  Command: " + self.command)
        print("  Path: " + self.path)
        path = self.path

        if path == '' or path == '/' or path == '/main_page.html':
            f = open('main_page.html', 'r')
            main_contents = f.read()
            f.close()

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(main_contents)))
            self.end_headers()
            self.wfile.write(str.encode(main_contents))

        elif path.startswith('/listSpecies'):
            server = "http://rest.ensembl.org"
            ext = "/info/species?"
            r = requests.get(server + ext, headers={"Content-Type": "application/json"})

            data = r.json()
            species_list = data['species']

            ls_main = open('ls_main.html', 'r')
            ls_menu = ls_main.read()
            ls_main.close()

            ls_response1 = open('ls_response1.html', 'r')
            ls_contents = ls_response1.read()
            ls_response1.close()

            if path == '/listSpecies?limit=':
                for x in species_list:
                    ls_contents += '<p>' + x['name'] + '<p>'

            elif path.startswith('/listSpecies?limit=') and self.path != '/listSpecies?limit=':
                limit = path.split('=')
                limit_num = limit[1]

                if not limit_num.isdigit():
                    print("Not a digit")
                    f = open('ls_error.html', 'r')
                    ls_contents = f.read()
                    f.close()

                else:
                    species_count = 0
                    for i in species_list:
                        ls_contents += '<p>' + i['name'] + '<p>'
                        species_count += 1
                        if str(species_count) == limit[1]:
                            break
                ls_contents += '<p>' + '\n' + '<p>'

            else:
                ls_contents = ls_menu

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(ls_contents)))
            self.end_headers()
            self.wfile.write(str.encode(ls_contents))

        elif path.startswith('/karyotype'):
            server = "http://rest.ensembl.org"
            ext = "/info/species?"
            r = requests.get(server + ext, headers={"Content-Type": "application/json"})

            data = r.json()
            species_list = data['species']

            kt_main = open('kt_main.html', 'r')
            kt_menu = kt_main.read()
            kt_main.close()

            kt_response = open('kt_response.html', 'r')
            kt_contents = kt_response.read()
            kt_response.close()

            if path == '/karyotype?species=':
                f = open('ls_error.html', 'r')
                kt_contents = f.read()
                f.close()

            elif path.startswith('/karyotype?species=') and path != '/karyotype?species=':
                species_name = path.split('=')
                species = species_name[1]
                print(species)

                if species not in species_list:
                    f = open('ls_error.html', 'r')
                    kt_contents = f.read()
                    f.close()

                elif species in species_list:
                    karyotype_ind = int()
                    for x in species_list:
                        if x['species'] == species:
                            karyotype_ind = x
                            break
                    karyotype_num = karyotype_list[karyotype_ind]
                    kt_contents += '<p>' + 'The karyotype for the species' + str(species) + 'is:' + str(karyotype_num) + '<p>'

            else:
                kt_contents = kt_menu

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(kt_contents)))
            self.end_headers()
            self.wfile.write(str.encode(kt_contents))

        # elif path.startswith('/chromosomeLength'):

        # else:
        # f = open('error', 'r')


Handler = TestHandler

# -- Open the socket server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at PORT", PORT)

    # -- Main loop: Attend the client. Whenever there is a new
    # -- clint, the handler is called
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("")
        print("Stoped by the user")
        httpd.server_close()

print("")
print("Server Stopped")
