import argparse
import os
import json

import json
import os
import subprocess
import sys
import datetime
import uuid


def get_random_id():
    the_id = uuid.uuid4()
    return str(the_id)


class mjdb:
    def __init__(self, db_file_name="sshc_db.json"):
        self.db_file_name = db_file_name

    def create_db(self):
        try:
            if not os.path.exists(self.db_file_name):
                with open(self.db_file_name, 'a') as opened_db:
                    json.dump([], opened_db)
            return True
        except Exception as ex:
            print(ex)
            return False

    def insert_data(self, data):
        try:
            data["id"] = get_random_id()
            existing_data = self.read_all_data()
            to_insert = existing_data + [data]
            with open(self.db_file_name, 'w') as opened_db:
                json.dump(to_insert, opened_db)
            return True
        except Exception as ex:
            print(ex)
            return False

    def read_all_data(self):
        try:
            with open(self.db_file_name, 'r') as opened_db:
                to_return = json.load(opened_db)
            return to_return
        except Exception as ex:
            print(ex)
            return False


def cleanup_file(configfile):
    configfiledir = configfile.replace("/" + configfile.split("/")[-1], "")

    try:
        os.remove(configfile)
    except Exception as ex:
        if len(configfile.split("/")) > 2:
            os.mkdir(configfiledir)
        with open(configfile, "w") as of:
            of.write("")


def insert_timestamp_into_configfile(configfile):
    dt_now = str(datetime.datetime.now(tz=datetime.timezone(offset=datetime.timedelta(hours=6))))
    with open(configfile, "a") as of:
        of.write("# Generated at: " + dt_now)
        of.write("\n")


def generate_host_entry_string(name, host, port, user, log_level, compression, idf, configfile, comment):
    entry_template = f'''\n# -- <
Host {name}
HostName {host}
Port {port}
User {user}
IdentityFile {idf}
LogLevel {log_level}
Compression {compression}
# Comment: {comment}
# -- >
\n'''

    with open(file=configfile, mode="a") as thefile:
        thefile.write(entry_template)


def read_list_of_hosts(db_file_name="sshc_db.json"):
    all_data = mjdb(db_file_name=db_file_name).read_all_data()
    to_return = ''''''
    for ii, i in enumerate(all_data):
        entry_template = f'''{ii+1}. {i["name"]} {i["host"]} {i["port"]} {i["user"]} {i["idf"]} {i["log_level"]} {i["compression"]} {i["comment"]}\n'''
        to_return += entry_template
    return to_return


def get_host_by_host_number(hn, db_file_name="sshc_db.json"):
    the_index = hn-1
    all_data = mjdb(db_file_name=db_file_name).read_all_data()
    return all_data[the_index]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SSH Config Generator !')
    mg1 = parser.add_mutually_exclusive_group(required=True)

    mg1.add_argument("--init", choices=["yes", "no"], help="Initialize DB?")
    mg1.add_argument("--insert", choices=["yes", "no"], help="Insert data?")
    mg1.add_argument("--generate", choices=["yes", "no"], help="Generate SSH Config from Database?")
    mg1.add_argument("--connect", choices=["yes", "no"], help="Where to make SSH connection? Choose host.")

    parser.add_argument('--name', help='Server Name?')
    parser.add_argument('--host', help='SSH Host?')
    parser.add_argument('--user', help='SSH User?', default="root")
    parser.add_argument('--port', help='SSH Port?', default=22)
    parser.add_argument('--idf', help='SSH Identity File?', default="~/.ssh/id_rsa")
    parser.add_argument('--comment', help='SSH Identity File?', default="No Comment.")
    parser.add_argument('--configfile', help='SSH Config File?', default="~/.ssh/config")

    parser.add_argument("--hn", help="Which Host by giving Host Number?")

    args = parser.parse_args()

    idf = args.idf
    configfile = args.configfile
    # user_home = os.path.expanduser("~")
    user_home = "."
    if "~" in idf:
        idf = idf.replace("~", user_home)
    if "~" in configfile:
        configfile = configfile.replace("~", user_home)

    if args.init == "yes":
        print("Initializing Database...")
        mjdb().create_db()
        print("Done.")

    elif args.insert == "yes":
        name = str(args.name).lower()
        host = args.host
        port = int(args.port)
        user = args.user
        comment = args.comment

        if not name or not host or not port or not user:
            exit("Some required parameters missing.")

        data = {
            "name": name, "host": host, "port": port, "user": user,
            "log_level": "DEBUG", "compression": "yes", "idf": idf,
            "comment": comment
        }
        print("Inserting data...")
        mjdb().insert_data(data=data)
        print("Done.")

    elif args.generate == "yes":
        print("Generating SSH Config File...")
        the_data = mjdb().read_all_data()
        if the_data:
            cleanup_file(configfile=configfile)
            insert_timestamp_into_configfile(configfile=configfile)
            for i in the_data:
                generate_host_entry_string(name=i["name"], host=i["host"], port=i["port"],
                                           user=i["user"], log_level=i["log_level"],
                                           compression=i["compression"], idf=i["idf"],
                                           configfile=configfile, comment=i["comment"]
                                       )
            print("Done.")
        else:
            exit("No data in DB.")

    elif args.connect == "yes":
        print_hosts = read_list_of_hosts()
        hn = args.hn
        if not hn:
            print(print_hosts)
            hn = input("Insert You choice of Host by Number to Connect to: ")

        host_info_by_hn = get_host_by_host_number(hn=int(hn))

        # print(f'Connecting to: {host_info_by_hn["host"]}')
        # subprocess.Popen(['ssh', '-tt', f'{host_info_by_hn["user"]}@{host_info_by_hn["host"]}',
        #                   '-p', f'{host_info_by_hn["port"]}'], shell=True)

        print(f'{host_info_by_hn["name"]}')
