from lxml import etree
import sys
import pdb
from glob import glob
import csv
import os
from os import listdir
from os.path import isfile, join
import subprocess
import base64
import time
import re
import smtplib
import argparse
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import bagit
from decimal import *
from sys import platform as _platform
getcontext().prec = 4


parser = argparse.ArgumentParser(description='Unencrypted DCP to H264 transcoder.'
                                 ' Written by Kieran O\'Leary.')
parser.add_argument('input')
'''
parser.add_argument(
                    '-bag', 
                    action='store_true',help='bag the dcp_dir if it passes the hash check')
'''
parser.add_argument(
                    '-m', 
                    action='store_true',help='send email report')

parser.add_argument(
                    '-s', 
                    action='store_true',help='Burn in subtitles')
args = parser.parse_args()
'''
if args.bag:
    bagging = 'enabled'
else:
    bagging = 'disabled'
'''

if args.m:
    email = 'enabled'
else:
    email = 'disabled'
    
#bagrm =  os.path.abspath('bag-rm.py') 
#bagit =  os.path.abspath('bagit.py') 
#print bagrm
dcp_dir = args.input

video_concat_filename = os.path.basename(dcp_dir) + '_video_concat' + time.strftime("_%Y_%m_%dT%H_%M_%S")
#video_concat_textfile = video_concat_textfile
audio_concat_filename = os.path.basename(dcp_dir) + '_audio_concat' + time.strftime("_%Y_%m_%dT%H_%M_%S")
if _platform == "win32":
    video_concat_textfile= os.path.expanduser("~\Desktop\%s.txt") % video_concat_filename
    audio_concat_textfile= os.path.expanduser("~\Desktop\%s.txt") % audio_concat_filename
else:
    video_concat_textfile= os.path.expanduser("~/Desktop/%s.txt") % video_concat_filename
    audio_concat_textfile= os.path.expanduser("~/Desktop/%s.txt") % audio_concat_filename


output_filename = os.path.basename(dcp_dir) + '_muxed' + time.strftime("_%Y_%m_%dT%H_%M_%S")
outputmkv= os.path.expanduser("~/Desktop/%s.mkv") % output_filename


# Two csv functions. One to create a csv, the other to add info to.


# Create a new .csv file with headings.  
# CSV filename will be DCp directory name + time/date.

# CSV will be saved to your Desktop.



for root,dirnames,filenames in os.walk(dcp_dir):
    if ("ASSETMAP.xml"  in filenames) or ("ASSETMAP"  in filenames) :
        dir = root

        filenoext = os.path.splitext(os.path.dirname(root))[0]

        # Change directory to directory with video files.
        # Changing directory makes globbing easier (from my experience anyhow).
        os.chdir(dir)

        # Scan the main DCP directory for an assetmap.
        dcp_files = [f for f in listdir(dir) if isfile(join(dir, f))]
        if 'ASSETMAP' in dcp_files:
            assetmap = 'ASSETMAP'
        elif 'ASSETMAP.xml' in dcp_files:
            assetmap = 'ASSETMAP.xml'

        # Parse the assetmap in order to find the namespace.  
        try:  
            assetmap_xml = etree.parse(assetmap)
        except SyntaxError:

            print 'not an assetmap!!!!'
            continue
           
        assetmap_namespace = assetmap_xml.xpath('namespace-uri(.)')     

        # Get a list of all XML files in the main DCP directory.
        xmlfiles = glob('*.xml')

        # Generate an empty list as there may be multiple PKLs.
        pkl_list = []

        # Loop through xmlfiles in order to find any PKL files.
        for i in xmlfiles:
            try:  
                xmlname = etree.parse(i)
            except SyntaxError:
                print 'not a valid PKL!!!!'
                continue
            except KeyError:
                print 'Missing PKL!!!!'
                continue
            
            is_pkl = xmlname.xpath('namespace-uri(.)')
            if 'CPL' in is_pkl:
                pkl_list.append(i)
            
        if len(pkl_list) == 0:
            continue
              
        # Generate an empty dictionary that will link the PKL hashes to each UUID.        
        pkl_hashes = {}

        # Loop through the PKLs and link each hash to a UUID.

        for i in pkl_list: 
            cpl_parse = etree.parse(i)
            pkl_namespace = cpl_parse.xpath('namespace-uri(.)') 

            xmluuid =  cpl_parse.findall('//ns:MainPicture/ns:Id',namespaces={'ns': pkl_namespace})
            xmluuid_audio =  cpl_parse.findall('//ns:MainSound/ns:Id',namespaces={'ns': pkl_namespace})
            xmluuid_subs =  cpl_parse.findall('//ns:MainSubtitle/ns:Id',namespaces={'ns': pkl_namespace})
            duration_image =  cpl_parse.findall('//ns:MainPicture/ns:Duration',namespaces={'ns': pkl_namespace})
            duration_audio =  cpl_parse.findall('//ns:MainSound/ns:Duration',namespaces={'ns': pkl_namespace})
            intrinsic_image=  cpl_parse.findall('//ns:MainPicture/ns:IntrinsicDuration',namespaces={'ns': pkl_namespace})
            intrinsic_audio=  cpl_parse.findall('//ns:MainSound/ns:IntrinsicDuration',namespaces={'ns': pkl_namespace})
            entry_image=  cpl_parse.findall('//ns:MainPicture/ns:EntryPoint',namespaces={'ns': pkl_namespace})
            entry_audio=  cpl_parse.findall('//ns:MainSound/ns:EntryPoint',namespaces={'ns': pkl_namespace})

        count = cpl_parse.xpath('count(//ns:MainPicture/ns:EntryPoint)',namespaces={'ns': pkl_namespace} )
        
        audio_delay = {}


 
        # Begin analysis of assetmap xml.

        counter = 0
        assetmap_paths =  assetmap_xml.findall('//ns:Path',namespaces={'ns': assetmap_namespace})
        assetmap_uuids =  assetmap_xml.findall('//ns:Asset/ns:Id',namespaces={'ns': assetmap_namespace})
        #while counter <= len(assetmap_paths) -1 :
            
        counter = 0

        file_paths = {}
        
        while counter <= len(assetmap_paths) -1 :

            if 'file:///' in assetmap_paths[counter].text:
                remove_this = 'file:///'
                assetmap_paths[counter].text =  assetmap_paths[counter].text.replace(remove_this,"")
            elif 'file://' in assetmap_paths[counter].text:
                remove_this = 'file://'
                assetmap_paths[counter].text =  assetmap_paths[counter].text.replace(remove_this,"")            

            elif 'file:/' in assetmap_paths[counter].text:
                remove_this = 'file:/'
                assetmap_paths[counter].text =  assetmap_paths[counter].text.replace(remove_this,"")
            

            file_paths[assetmap_uuids[counter].text] = [assetmap_paths[counter].text] # {assetmapuuid:assetmapfilename}
            counter +=1
        pic_mxfs = [] 
          
        for yes in xmluuid:
            for blabla in file_paths[yes.text]:    
        
                pic_mxfs.append(blabla)
                 
        aud_mxfs = []   
        for yes in xmluuid_audio:
            for blabla in file_paths[yes.text]:    
        
                aud_mxfs.append(blabla)


        subs = []   
        for yes in xmluuid_subs:
            for blabla in file_paths[yes.text]:    
        
                subs.append(blabla)
        
        if args.s:
            print pic_mxfs
            print subs
            print xmluuid_subs
            sys.exit()
        count = cpl_parse.xpath('count(//ns:MainSound/ns:EntryPoint)',namespaces={'ns': pkl_namespace} )
        
        counter = 1
        delays = 0
        while counter <= count:
            
            audio_delay_values = []
            
            xmluuid =  cpl_parse.xpath('//ns:MainSound[%s]/ns:Id' % counter,namespaces={'ns': pkl_namespace})
                      
            EntryPoint =  cpl_parse.xpath('//ns:MainSound[%s]/ns:%s '% (counter, 'EntryPoint'),namespaces={'ns': pkl_namespace}) 
            entrypoint_audio = float(EntryPoint[0].text)
            if EntryPoint[0].text != '0':
                delays += 1
                entrypoint_audio = float(EntryPoint[0].text) 
                entrypoint_audio = float(entrypoint_audio) / 24.000
                entrypoint_audio = round(entrypoint_audio, 3)
            audio_delay_values.append(entrypoint_audio) 
            dur =  cpl_parse.xpath('//ns:MainSound[%s]/ns:%s '% (counter, 'Duration'),namespaces={'ns': pkl_namespace})
            dur_intrinsic =  cpl_parse.xpath('//ns:MainSound[%s]/ns:%s '% (counter, 'IntrinsicDuration'),namespaces={'ns': pkl_namespace})
             
            tail_test = int(dur_intrinsic[0].text) - int(dur[0].text)

            if tail_test > 0:
                delays +=1


            tail_delay = int(dur[0].text)
            tail_delay = float(tail_delay) / 24.000
            tail_delay = round(tail_delay, 3)
         
            audio_delay_values.append(tail_delay)
            audio_delay_values.append(file_paths[xmluuid[0].text][0])
            #audio_delay_values.append(dur[0].text)
            audio_delay[xmluuid[0].text] = audio_delay_values
            counter += 1 

        if _platform == "win32":
            print 'windows'
            dir_append = args.input + '\\'
            concat_string = 'file \'' 
            concat_append = '\''
        else:
            dir_append = args.input + '/'
            concat_string = 'file \'' 
            concat_append = '\''
        picture_files_fix1 = [dir_append + x for x in pic_mxfs]
        # http://stackoverflow.com/a/2050721/2188572
        picture_files_fix2 = [concat_string + x for x in picture_files_fix1]
        finalpic = [x + concat_append for x in picture_files_fix2]
        if delays == 0:

            audio_files_fix1 = [dir_append + x  for x in aud_mxfs]
        else:
            audio_files_fix1 = [dir_append + x + '.mkv' for x in aud_mxfs]
        # http://stackoverflow.com/a/2050721/2188572
        audio_files_fix2 = [concat_string + x for x in audio_files_fix1]
        finalaudio = [x + concat_append for x in audio_files_fix2]
        print finalaudio
        if delays == 0:
            print 'there were no delays'
        else:
            for i in audio_delay:
                print audio_delay[i][2]
                print audio_delay[i][1]
                
                subprocess.call(['ffmpeg','-ss',str(audio_delay[i][0]),'-i',audio_delay[i][2],'-t',str(audio_delay[i][1]),'-c:a','copy', audio_delay[i][2] + '.mkv'])
    
        
        # Write the list of filenames containing picture to a textfile. 
        # http://www.pythonforbeginners.com/files/reading-and-writing-files-in-python
        def write_textfile(textfile, list_type):
            file = open(textfile, "w")
            for item in list_type:
              file.write("%s\n" % item)
            file.close()  # ffmpeg can't access the textfile until it's closed.

        write_textfile(video_concat_textfile, finalpic)
        write_textfile(audio_concat_textfile, finalaudio)

        if args.s:
            print 'subs placeholder'
        else:    
            command = ['ffmpeg','-f','concat','-safe', '0',
                       '-i',video_concat_textfile,'-f','concat','-safe', '0',
                       '-i',audio_concat_textfile,'-c:v','libx264', 
                       '-pix_fmt', 'yuv420p', '-crf','21',
                       '-c:a','aac',outputmkv ]

            subprocess.call(command)
        
        # Removes PKLs from list of files to hash, as these files are not in manifest.


if email == 'enabled': 
    emailfrom = ""
    emailto = ['', '']
    #emailto = ", ".join(emailto)
    fileToSend = ''
    username = ""
    password = ""

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = ", ".join(emailto)
    msg["Subject"] = "Hash check complete"
    msg.preamble = "testtesttest"
    body = MIMEText("example email body")
    msg.attach(body)

    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)

    if maintype == "text":
        fp = open(fileToSend)
        # Note: we should handle calculating the charset
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "image":
        fp = open(fileToSend, "rb")
        attachment = MIMEImage(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == "audio":
        fp = open(fileToSend, "rb")
        attachment = MIMEAudio(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(fileToSend, "rb")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    msg.attach(attachment)


    server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server_ssl.ehlo() # optional, called by login()
    server_ssl.login(username, password)  
    # ssl server doesn't support or need tls, so don't call server_ssl.starttls() 
    server_ssl.sendmail(emailfrom, emailto, msg.as_string())
    print msg.as_string()
    #server_ssl.quit()
    server_ssl.close()
    print 'successfully sent the mail'    