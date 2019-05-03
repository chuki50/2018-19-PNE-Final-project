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
            species_info = data['species']
            name_list = []
            for x in species_info:
                name_list.append(x['name'])

            kt_main = open('kt_main.html', 'r')
            kt_menu = kt_main.read()
            kt_main.close()

            kt_response = open('kt_response.html', 'r')
            kt_contents = kt_response.read()
            kt_response.close()

            if path == '/karyotype?specie=':
                f = open('kt_error.html', 'r')
                kt_contents = f.read()
                f.close()

            elif path.startswith('/karyotype?specie=') and path != '/karyotype?specie=':
                species_r = path.split('=')
                species_name = species_r[1]
                print(species_name)

                server = "http://rest.ensembl.org"
                ext = "/info/assembly/{}?".format(species_name)
                r2 = requests.get(server + ext, headers={"Content-Type": "application/json"})

                data2 = r2.json()

                if species_name not in name_list:
                    f = open('kt_error.html', 'r')
                    kt_contents = f.read()
                    f.close()

                elif species_name in name_list:
                    karyotype = ""
                    kt_contents += '<p>' + 'The karyotype for the species ' + str(species_name) + ' is: ' + '<p>'
                    for k in data2['karyotype']:
                        print(k)
                        karyotype = str(k)
                        kt_contents += '<p>' + karyotype + '<p>'

            else:
                kt_contents = kt_menu

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(kt_contents)))
            self.end_headers()
            self.wfile.write(str.encode(kt_contents))

        elif path.startswith('/chromosomeLength'):
            server = "http://rest.ensembl.org"
            ext = "/info/species?"
            r = requests.get(server + ext, headers={"Content-Type": "application/json"})

            data = r.json()
            species_info = data['species']
            name_list = []
            for x in species_info:
                name_list.append(x['name'])

            cl_main = open('cl_main.html', 'r')
            cl_menu = cl_main.read()
            cl_main.close()

            cl_response = open('cl_response.html', 'r')
            cl_contents = cl_response.read()
            cl_response.close()

            if path == '/chromosomeLength?specie=&chromo=':
                f = open('cl_error1.html', 'r')
                cl_contents = f.read()
                f.close()

            elif path.startswith('/chromosomeLength?specie='):
                species_r = path.split('=')
                species_r1 = species_r[1]

                chromo_r = species_r[2]
                chromo_chosen = str(chromo_r)
                print(chromo_chosen)

                species_r2 = str(species_r1)
                species_name = species_r2.split('&')[0]
                print(species_name)

                server = "http://rest.ensembl.org"
                ext = "/info/assembly/{}?".format(species_name)
                r3 = requests.get(server + ext, headers={"Content-Type": "application/json"})

                data3 = r3.json()

                if species_name not in name_list:
                    f = open('kt_error.html', 'r')
                    cl_contents = f.read()
                    f.close()

                elif species_name in name_list:
                    chromo_len = ''
                    for x in data3['top_level_region']:
                        if x['name'] == chromo_chosen:
                            chromo_len = x['length']
                            print(chromo_len)
                            break

                    if chromo_len == '0' or chromo_len == '':
                        f = open('cl_error2.html', 'r')
                        cl_contents = f.read()
                        f.close()

                    else:
                        cl_contents += '<p>' + 'The chromosome length for the chromosome ' + str(chromo_chosen)
                        cl_contents += ' of the species ' + str(species_name) + ' is: ' + str(chromo_len) + '<p>'


            else:
                cl_contents = cl_menu

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(cl_contents)))
            self.end_headers()
            self.wfile.write(str.encode(cl_contents))

        else:
            f = open('main_error.html', 'r')
            error_msg = f.read()
            f.close()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(error_msg)))
            self.end_headers()
            self.wfile.write(str.encode(error_msg))



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
        print("Stopped by the user")
        httpd.server_close()

print("")
print("Server Stopped")
