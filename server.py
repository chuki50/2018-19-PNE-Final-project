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
            # This option allows us to obtain a list of species from the ensemble project.
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

        elif path.startswith('/geneSeq'):
            # This option allows us to obtain the whole sequence of a gene we decide.

            gs_main = open('gs_main.html', 'r')
            gs_menu = gs_main.read()
            gs_main.close()

            gs_response = open('gs_response.html', 'r')
            gs_contents = gs_response.read()
            gs_response.close()

            if path == '/geneSeq?gene=':
                # This error is returned if the gene is empty.
                gs_error1 = open('gs_error1.html', 'r')
                gs_contents = gs_error1.read()
                gs_error1.close()

            elif path.startswith('/geneSeq?gene='):
                gene_r = path.split('=')
                gene_chosen = gene_r[1]

                server = "http://rest.ensembl.org"
                ext = "/lookup/symbol/homo_sapiens/{}?".format(gene_chosen)
                r4 = requests.get(server + ext, headers={"Content-Type": "application/json"})
                data4 = r4.json()

                try:
                    seq_id = data4['id']
                    server = "http://rest.ensembl.org"
                    ext = "/sequence/id/{}?".format(seq_id)
                    r4_1 = requests.get(server + ext, headers={"Content-Type": "application/json"})
                    data4_1 = r4_1.json()

                    seq = data4_1['seq']
                    gs_contents += '<p>' + 'The sequence of the gene ' + str(gene_chosen) + ' is: '
                    gs_contents += str(seq) + '<p>'

                except KeyError:
                    # This will happen if the gene introduced isn't valid. It's quicker this way.
                    gs_error2 = open('gs_error2.html', 'r')
                    gs_contents = gs_error2.read()
                    gs_error2.close()

            else:
                gs_contents = gs_menu

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(gs_contents)))
            self.end_headers()
            self.wfile.write(str.encode(gs_contents))

        elif path.startswith('/geneInfo'):
            # This option allows us to obtain the start and end point of a gene, and also the length, the ID and the
            # chromosome it is in.

            gi_main = open('gi_main.html', 'r')
            gi_menu = gi_main.read()
            gi_main.close()

            gi_response = open('gi_response.html', 'r')
            gi_contents = gi_response.read()
            gi_response.close()

            if path == '/geneInfo?gene=':
                # As we did with geneSeq, this error is returned when the gene parameter is empty.
                gs_error1 = open('gs_error1.html', 'r')
                gi_contents = gs_error1.read()
                gs_error1.close()

            elif path.startswith('/geneInfo?gene='):

                gene_r = path.split('=')
                gene_chosen = gene_r[1]

                server = "http://rest.ensembl.org"
                ext = "/lookup/symbol/homo_sapiens/{}?".format(gene_chosen)
                r4 = requests.get(server + ext, headers={"Content-Type": "application/json"})
                data4 = r4.json()

                server = "http://rest.ensembl.org"
                ext = "/lookup/symbol/homo_sapiens/{}?".format(gene_chosen)
                r5 = requests.get(server + ext, headers={"Content-Type": "application/json"})
                data5 = r5.json()

                try:
                    seq_id = data4['id']
                    server = "http://rest.ensembl.org"
                    ext = "/sequence/id/{}?".format(seq_id)
                    r4_1 = requests.get(server + ext, headers={"Content-Type": "application/json"})
                    data4_1 = r4_1.json()

                    seq = data4_1['seq']
                    gene_length = len(seq)

                    seq_id = data5['id']

                    server = "http://rest.ensembl.org"
                    ext = "/lookup/id/{}?".format(seq_id)
                    r5_1 = requests.get(server + ext, headers={"Content-Type": "application/json"})

                    data5_1 = r5_1.json()
                    gene_start = data5_1['start']
                    gene_end = data5_1['end']
                    gene_id = data5_1['id']
                    gene_chromo = data5_1['seq_region_name']

                    gi_contents += '<p>' + '          Start: ' + str(gene_start) + '<p>' + '\r\n'
                    gi_contents += '<p>' + '            End: ' + str(gene_end) + '<p>' + '\r\n'
                    gi_contents += '<p>' + '             ID: ' + str(gene_id) + '<p>' + '\r\n'
                    gi_contents += '<p>' + '         Length: ' + str(gene_length) + '<p>' + '\r\n'
                    gi_contents += '<p>' + '     Chromosome: ' + str(gene_chromo) + '<p>' + '\r\n'

                except KeyError:
                    # As we also did in geneSeq, this error is returned when the gene is invalid.

                    gs_error2 = open('gs_error2.html', 'r')
                    gi_contents = gs_error2.read()
                    gs_error2.close()

            else:
                gi_contents = gi_menu

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(gi_contents)))
            self.end_headers()
            self.wfile.write(str.encode(gi_contents))

        elif path.startswith('/geneCalc'):
            # This option allows the user to analyze the percentages of the bases in the gene sequence of a gene that's
            # given by the user.

            gc_main = open('gc_main.html', 'r')
            gc_menu = gc_main.read()
            gc_main.close()

            gc_response = open('gc_response.html', 'r')
            gc_contents = gc_response.read()
            gc_response.close()

            if path == '/geneCalc?gene=':
                # As we did with geneSeq and geneInfo, this error is returned when the gene parameter is empty.
                gs_error1 = open('gs_error1.html', 'r')
                gc_contents = gs_error1.read()
                gs_error1.close()

            elif path.startswith('/geneCalc?gene='):

                gene_r = path.split('=')
                gene_chosen = gene_r[1]

                server = "http://rest.ensembl.org"
                ext = "/lookup/symbol/homo_sapiens/{}?".format(gene_chosen)
                r6 = requests.get(server + ext, headers={"Content-Type": "application/json"})
                data6 = r6.json()

                try:
                    seq_id = data6['id']
                    server = "http://rest.ensembl.org"
                    ext = "/sequence/id/{}?".format(seq_id)
                    r6_1 = requests.get(server + ext, headers={"Content-Type": "application/json"})
                    data6_1 = r6_1.json()

                    seq = data6_1['seq']
                    seq_length = len(seq)
                    a_count = 0
                    g_count = 0
                    c_count = 0
                    t_count = 0
                    for x in range(len(seq)):
                        if seq[x] == "A":
                            a_count += 1
                        elif seq[x] == "G":
                            g_count += 1
                        elif seq[x] == "C":
                            c_count += 1
                        elif seq[x] == "T":
                            t_count += 1
                    a_perc = round(100 * (a_count / seq_length))
                    g_perc = round(100 * (g_count / seq_length))
                    c_perc = round(100 * (c_count / seq_length))
                    t_perc = round(100 * (t_count / seq_length))

                    gc_contents += '<p>' + 'Length: ' + str(seq_length) + ' bases' + '<p>' + '\r\n'
                    gc_contents += '<p>' + 'Number of bases: '
                    gc_contents += 'A: {}  G: {}  C: {}  T: {} '.format(a_count, g_count, c_count, t_count) + '<p>'
                    gc_contents += '\r\n' + '<p>' + 'Percentages of bases: '
                    gc_contents += 'A: {}%  G: {}%  C: {}%  T: {}% '.format(a_perc, g_perc, c_perc, t_perc) + '<p>'

                except KeyError:
                    # Again, this error is returned when the gene  is invalid.
                    gs_error2 = open('gs_error2.html', 'r')
                    gc_contents = gs_error2.read()
                    gs_error2.close()

            else:
                gc_contents = gc_menu

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(gc_contents)))
            self.end_headers()
            self.wfile.write(str.encode(gc_contents))

        elif path.startswith('/geneList'):
            # This option will tell us what genes are in a certain chromosome, and the user can introduce an upper and
            # lower bound as limits.
            gl_main = open('gl_main.html', 'r')
            gl_menu = gl_main.read()
            gl_main.close()

            gl_response = open('gl_response.html', 'r')
            gl_contents = gl_response.read()
            gl_response.close()

            if path.startswith('/geneList?chromo=&'):
                # This error is returned when the chromosome is empty.
                gl_error1 = open('gl_error1.html', 'r')
                gl_contents = gl_error1.read()
                gl_error1.close()

            elif path.startswith('/geneList?chromo='):
                path_r = path.split('?')
                path_r1 = str(path_r).split('=')
                try:
                    path_r21 = path_r1[1]
                    path_r22 = path_r1[2]
                    path_r33 = path_r1[3]

                    path_r31 = path_r21.split('&')
                    chromo = path_r31[0]

                    path_r32 = path_r22.split('&')
                    start = path_r32[0]

                    end = path_r33.split('\'')[0]

                    server = "http://rest.ensembl.org"
                    ext_r = "/overlap/region/human/{}:{}-{}?".format(chromo, start, end)
                    ext = ext_r + "feature=gene;" \
                                  ""
                    r = requests.get(server + ext, headers={"Content-Type": "application/json"})
                    data7 = r.json()

                    gl_contents += '<p>' + 'In the chromosome ' + str(chromo) + ' and between'
                    gl_contents += ' {} and {}'.format(start, end) + ' we find:' + '<p>\r\n'
                    count = 0
                    for x in data7:
                        type = x['feature_type']
                        if type == 'gene':
                            gl_contents += '<p>' + x['external_name'] + '<p>\r\n'
                            count += 1

                    gl_contents += '<p>' + 'There are a total of {} genes in between'.format(count) + '<p>\r\n'

                except TypeError:
                    # This error is return when the limit parameters are not numbers. It will also pop up if your
                    # chromosome is not reachable or invalid.
                    gl_error2 = open('gl_error2.html', 'r')
                    gl_contents = gl_error2.read()
                    gl_error2.close()

            else:
                gl_contents = gl_menu

            print(gl_contents)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(gl_contents)))
            self.end_headers()
            self.wfile.write(str.encode(gl_contents))

        else:
            # This error pops up only if you try to introduce something invalid in the URL,
            # such as localhost:8000/hello, localhost:8000/menu, etc. However, it has a link to the main menu.

            f = open('main_error.html', 'r')
            error_msg = f.read()
            f.close()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(str.encode(error_msg)))
            self.end_headers()
            self.wfile.write(str.encode(error_msg))


Handler = TestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("Serving at PORT", PORT)

    # -- Main loop: Attend the client. Whenever there is a new
    # -- client, the handler is called
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Stopped by the user")
        httpd.server_close()
