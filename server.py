import http.server
import socketserver
import termcolor
import requests

socketserver.TCPServer.allow_reuse_address = True

PORT = 8000


class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        print("GET received! Request line:")
        termcolor.cprint("  " + self.requestline, 'cyan')
        print("  Command: " + self.command)
        print("  Path: " + self.path)
        path = self.path

        if path == '' or path == '/' or path == '/main_page.html':
            # We are going to open the main page, which will act as a menu where we can choose what we want to do.
            # I have decided to have different menu pages for all the options instead of having them in the main menu.
            # That way, it's more organized. However, in each of them, you'll get the option to go back to the menu.

            f = open('main_page.html', 'r')
            main_contents = f.read()
            f.close()

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(main_contents)))
            self.end_headers()
            self.wfile.write(str.encode(main_contents))

        elif path.startswith('/listSpecies'):
            # This resource allows us to obtain a list of species from the ensemble project.
            # We can get all of them or just a few with the limit parameter

            # In order to connect to the server, we are going to need to use the requests resource.
            # The next procedure is the one provided by the website of the ENSEMBL endpoints for Python3.

            # We are going to be using this same procedure for the rest of the practice:
            # We use the requests to connect to the server and then we gather all the data we need from it.
            # Since its format is json, we are going to specify in that manner.

            server = "http://rest.ensembl.org"
            ext = "/info/species?"
            r = requests.get(server + ext, headers={"Content-Type": "application/json"})

            data = r.json()
            species_list = data['species']

            ls_main = open('ls_main.html', 'r')
            ls_menu = ls_main.read()
            ls_main.close()

            ls_response = open('ls_response.html', 'r')
            ls_contents = ls_response.read()
            ls_response.close()

            if path == '/listSpecies?limit=':
                # If the limit parameter is empty, we print all of the species.
                for x in species_list:
                    ls_contents += '<p>' + x['name'] + '<p>'
                    ls_contents += '\r\n'

            elif path.startswith('/listSpecies?limit=') and self.path != '/listSpecies?limit=':
                # If there is a limit , we need to check if it's valid.
                limit = path.split('=')
                limit_num = limit[1]

                if not limit_num.isdigit():
                    # The limit is not a digit, so we return an error explaining what happened in this case.
                    f = open('ls_error.html', 'r')
                    ls_contents = f.read()
                    f.close()

                else:
                    # Now that we have a limit, we are going to limit the number of species shown with
                    # the following loop. When the species_count variable reaches the limit, it will stop the loop.
                    species_count = 0
                    for i in species_list:
                        ls_contents += '<p>' + i['name'] + '<p>'
                        ls_contents += '\r\n'
                        species_count += 1
                        if str(species_count) == limit[1]:
                            break

            else:
                # When it's only /listSpecies, we return the menu for this option, where you can introduce the limit.
                ls_contents = ls_menu

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(ls_contents)))
            self.end_headers()
            self.wfile.write(str.encode(ls_contents))

        elif path.startswith('/karyotype'):
            # This option allows us to obtain the karyotype of a species we decide.

            server = "http://rest.ensembl.org"
            ext = "/info/species?"
            r = requests.get(server + ext, headers={"Content-Type": "application/json"})

            data = r.json()
            species_info = data['species']

            # In this case, we are making a list of species, so we can later make sure that the specie introduce is
            # a valid one. It's very simple.
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
                # When there is no specie specified, we return an error.
                f = open('kt_error.html', 'r')
                kt_contents = f.read()
                f.close()

            elif path.startswith('/karyotype?specie=') and path != '/karyotype?specie=':
                species_r = path.split('=')
                species_name = species_r[1]

                # We now connect to a different part of the ENSEMBL project. In this one, we will be able to find
                # the karyotype of the species. We follow almost the same procedure as mentioned in line 43.
                # We will also add the species to the ext, because we need it in order to get its karyotype.
                server = "http://rest.ensembl.org"
                ext = "/info/assembly/{}?".format(species_name)
                r2 = requests.get(server + ext, headers={"Content-Type": "application/json"})

                data2 = r2.json()

                # As mentioned before, we are going to make sure the species entered is valid.
                if species_name not in name_list:
                    f = open('kt_error.html', 'r')
                    kt_contents = f.read()
                    f.close()

                elif species_name in name_list:
                    kt_contents += '<p>' + 'The karyotype for the species ' + str(species_name) + ' is: ' + '<p>'
                    for k in data2['karyotype']:
                        karyotype = str(k)
                        kt_contents += '<p>' + karyotype + '<p>'
                        kt_contents += '\r\n'

            else:
                # When it's only /karyotype, we return the menu for this option, where you introduce the name of the
                # species whose karyotype you want to obtain
                kt_contents = kt_menu

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(kt_contents)))
            self.end_headers()
            self.wfile.write(str.encode(kt_contents))

        elif path.startswith('/chromosomeLength'):
            # This option will allow us to get the chromosome length of a chromosome of a species.
            # We have to both choose the species and chromosome we want to analyze.

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
                # In this error, the user hasn't introduced anything in the parameters. We send him an error page,
                # specifying what he did wrong.
                f = open('cl_error1.html', 'r')
                cl_contents = f.read()
                f.close()

            elif path.startswith('/chromosomeLength?specie='):
                # We use the '_r' to specify that is a 'rough draft' of what the variable will mean.
                species_r = path.split('=')
                species_r1 = species_r[1]

                chromo_r = species_r[2]
                chromo_chosen = str(chromo_r)

                species_r2 = str(species_r1)
                species_name = species_r2.split('&')[0]

                server = "http://rest.ensembl.org"
                ext = "/info/assembly/{}?".format(species_name)
                r3 = requests.get(server + ext, headers={"Content-Type": "application/json"})

                data3 = r3.json()

                if species_name not in name_list:
                    # We can reuse the error from the karyotype part, where the species was no on the list.
                    f = open('kt_error.html', 'r')
                    cl_contents = f.read()
                    f.close()

                elif species_name in name_list:
                    chromo_len = ''
                    for x in data3['top_level_region']:
                        if x['name'] == chromo_chosen:
                            chromo_len = x['length']
                            break

                    if chromo_len == '0' or chromo_len == '':
                        # If we get a null length, it means that the chromosome introduced didn't exist to begin with.
                        # So, we will return an error page that informs the user of it.
                        f = open('cl_error2.html', 'r')
                        cl_contents = f.read()
                        f.close()

                    else:
                        cl_contents += '<p>' + 'The chromosome length for the chromosome ' + str(chromo_chosen)
                        cl_contents += ' of the species ' + str(species_name) + ' is: ' + str(chromo_len) + '<p>'

            else:
                # If it's only /chromosomeLength, then it'll return the menu, in which you introduced both parameters.
                cl_contents = cl_menu

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(cl_contents)))
            self.end_headers()
            self.wfile.write(str.encode(cl_contents))

        else:
            # This error pops up only if you try to introduce something invalid in the URL,
            # such as localhost:8000/hello, localhost:8000/menu, etc. However, it has a link to the main menu.

            f = open('main_error.html', 'r')
            error_msg = f.read()
            f.close()
            print(error_msg)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(error_msg)))
            self.end_headers()
            self.wfile.write(str.encode(error_msg))


Handler = TestHandler
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
