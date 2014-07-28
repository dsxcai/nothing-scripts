import binascii
import os
import shutil
import optparse


def isBigZip(zipPath):        
    MAGIC_LENGTH = 8
    MAGIC_STR = "LaR@eZip"
    if not os.path.isfile(zipPath):
        return "Error: %s not exist" % zipPath            

    find = False

    f = open(zipPath, "rb")
    byte = f.read(MAGIC_LENGTH)
    #aalog.log(self.task_id, "byte=%s\n" %  byte)
    if byte == MAGIC_STR:
        find = True
    f.close()
    
    return find

def splitBigZip(zipPath, outputDir):
    MAGIC_LENGTH = 8
    MAX_ZIP_COUNT = 8
    HEAD_LENGTH = 256
    MAGIC_STR = "LaR@eZip"
    OFFSET = []
    ZIP_SIZE= []
    ZIP_NUMBER = 0

    split_zip_list = []

    #outputDir = os.path.dirname(zipPath)
    if os.path.isdir(outputDir):
        shutil.rmtree(outputDir)
    os.mkdir(outputDir)
        
    
    if not os.path.isfile(zipPath):
        return "Error: %s not exist" % zipPath
    
    f = open(zipPath, "rb")
    byte = f.read(MAGIC_LENGTH)
    if byte == MAGIC_STR:
        print "find magic..."
        for i in range(MAX_ZIP_COUNT):
            bytes = f.read(4)
            OFFSET.append(bytes)
        for i in range(MAX_ZIP_COUNT):
            bytes = f.read(4)
            ZIP_SIZE.append(bytes)
        ZIP_NUMBER = f.read(4)   
    f.close()
    
    print "OFFSET=%s" % OFFSET
    print "ZIP_SIZE=%s" % ZIP_SIZE  
    
    for i in range(MAX_ZIP_COUNT):
        OFFSET[i] = binascii.hexlify(OFFSET[i])
        ZIP_SIZE[i] = binascii.hexlify(ZIP_SIZE[i])
        print "OFFSET[%s]=%s" % ( i, OFFSET[i] )
        print "ZIP_SIZE[%s]=%s" % ( i, ZIP_SIZE[i] )
        
        print "============================================================="
        oldstr = OFFSET[i]
        newstr = oldstr[6:8] + oldstr[4:6] + oldstr[2:4] + oldstr[0:2]
        OFFSET[i] = newstr
        print "OFFSET[%s]=%s" % ( i, OFFSET[i] )
        print "============================================================="
        oldstr = ZIP_SIZE[i]
        newstr = oldstr[6:8] + oldstr[4:6] + oldstr[2:4] + oldstr[0:2]
        ZIP_SIZE[i] = newstr
        print "ZIP_SIZE[%s]=%s" % ( i, ZIP_SIZE[i] )
        print "============================================================="
        OFFSET[i] = int(OFFSET[i], 16)
        ZIP_SIZE[i] = int(ZIP_SIZE[i], 16)
        print "OFFSET[%s]=%s" % ( i, OFFSET[i] )
        print "ZIP_SIZE[%s]=%s" % ( i, ZIP_SIZE[i] )
        print "============================================================="

    print "switch to normal size...."
    print "OFFSET=%s" % OFFSET
        
    f = open(zipPath, "rb")
    for i in range(MAX_ZIP_COUNT):
        if OFFSET[i] != 0:
            partZip = os.path.join(outputDir, "zip_%s.zip" % i)
            print "writing %s...." % partZip
            f2 = file(partZip, 'wb')
            f.seek(OFFSET[i])
            f2.write(f.read(ZIP_SIZE[i]))
            f2.close
            split_zip_list.append(partZip)
    f.close()            
    return split_zip_list


if __name__ == '__main__':
    parser = optparse.OptionParser(usage="usage: python %prog [options] zipPath", version="splitZip 1.0")
    #parser.add_option('-s', '--source_zip', action="store", dest="zip_path", help='zip file we want to split')
    parser.add_option('-o', '--outputdir', action="store", dest="dist_dir", help='destination for extract images')
    parser.add_option('-z', '--ziponly', action="count", dest="zip_only", help='only need to extract to zip')
    parser.add_option("-v", "--verbose", action="count", dest="verbosity")
    (opts, args) = parser.parse_args()    

    if len(args) != 1:
        print "args=%s" % args
        parser.error("incorrect number of arguments")

    if opts.verbosity > 1:
        print "opts=%s" % opts    

    currentDir = os.getcwd()

    zipPath = os.path.join(currentDir, args[0])
    if not os.path.isfile(zipPath):
        parser.error("%s not exist... , please input exist zip file" % zipPath)

    outputDir = os.path.join(os.path.dirname(zipPath), "extract_imgs")
    if opts.dist_dir:
        if not os.path.isdir(opts.dist_dir):
            parser.error("%s not exist... , please input exist folder name" % opts.dist_dir)
    else:
        if os.path.isdir(outputDir):
            print "%s exist, program will clean this dir's content. Want to continue?" % outputDir

            while(1):
                var = raw_input("(y/n)?")
                if var == "y" or var == "Y":
                    break
                elif var == "n" or var == "N":
                    print "You could use -o option to extract images to that dir"
                    exit(0)

    # Start
    if not isBigZip(zipPath):
        print "%s is not multiple stage zip format!!!" % zipPath
        exit(0)
            
    # split
    retVal = splitBigZip(zipPath, outputDir)
    if str(retVal).startswith("Error:"):
        print retVal
        exit(1)
    if opts.zip_only:
        print "finish split to %s" % retVal
        exit(0)
        
    for zip in retVal:
        if not os.path.isfile(zip):
            print  "Error: %s not exist..." % zip
            exit(1)
        command = "unzip -o %s -d %s" % (zip, outputDir)
        os.system(command)
        os.remove(zip)
        
    # cat system.img back...
    system_list = []
    files = os.listdir(outputDir)
    for file in files:
        if str(file).startswith("system_") and str(file).endswith("img"):
            system_list.append(file)
        if str(file).startswith("android-info-1"):
            filepath = os.path.join(outputDir, file)
            os.remove(filepath)
    
    system_list.sort()
    print "system_list=%s" % system_list
    
    targetSysImgPath = os.path.join(outputDir, "system.img")
    for system_img in system_list:
        split_system_path = os.path.join(outputDir, system_img)
        command = ""
        if str(system_img).find("_1.img") >=0:
            command = "cat %s > %s" % (split_system_path, targetSysImgPath)
        else:
            command = "cat %s >> %s" % (split_system_path, targetSysImgPath)
        print command
        os.system(command)
        os.remove(split_system_path)
    
    print "Extract zip file finsh!!!"
    print "Images are under %s" % outputDir