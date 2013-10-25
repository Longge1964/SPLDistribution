'''
Created on 2013/10/25

@author: tshimizu
'''
import struct
import os

class Pressure:
    def __init__(self, geoName, pName, rho, t):
        self.geoName = geoName
        self.pName = pName
        self.rho = rho
        self.t = t
        self.tria_p = []
        self.quad_p = []
        self.nsided_p = []
        self.Max = rho * 27.78 * 27.78 * 0.5 * 2.0
        self.Min = -1.0 * rho * 27.78 * 27.78 * 0.5 * 4.0
        
    def readGeo(self):
        self.tria3 = 0
        self.quad4 = 0
        self.nsided = 0
        #--- read file for .geo
        inGeoFile = open(self.geoName,'r')
        for line in inGeoFile:
            if line.strip() == 'tria3':
                self.tria3 = inGeoFile.next().strip()
            if line.strip() == 'quad4':
                self.quad4 = inGeoFile.next().strip()
            if line.strip() == 'nsided':
                self.nsided = inGeoFile.next().strip()
        inGeoFile.close() 
        
    def getTria3(self):
        return self.tria3
    
    def getQuad4(self):
        return self.quad4
    
    def getNsided(self):
        return self.nsided
    
    def getTime(self):
        return self.t
    
    def getTriaP(self):
        return self.tria_p
    
    def getQuadP(self):
        return self.quad_p
    
    def getNsidedP(self):
        return self.nsided_p
    
    def readP(self):
        infile = open(self.pName, 'rb')
        print '1. signed char (80): %s' % struct.unpack('80s', infile.read(80))
        print '2. signed char (80): %s' % struct.unpack('80s', infile.read(80))
        print '3. int: %i' % struct.unpack('i', infile.read(4))
        if int(self.tria3) > 0:
            print '4. signed char (80): %s' % struct.unpack('80s', infile.read(80))
            for i in range(0, int(self.tria3)):
                b = struct.unpack('f', infile.read(4))
                for bb in b:
                    p = bb * self.rho
                    self.tria_p.append(max(self.Min, min(self.Max, p)))
        if int(self.quad4) > 0:
            print '6. signed char (80): %s' % struct.unpack('80s', infile.read(80))
            for i in range(0, int(self.quad4)):
                b = struct.unpack('f', infile.read(4))
                for bb in b:
                    p = bb * self.rho
                    self.quad_p.append(max(self.Min, min(self.Max, p)))
        if int(self.nsided) > 0:
            print '8. signed char (80): %s' % struct.unpack('80s', infile.read(80))
            for i in range(0, int(self.nsided)):
                b = struct.unpack('f', infile.read(4))
                for bb in b:
                    p = bb * self.rho
                    self.nsided_p.append(max(self.Min, min(self.Max, p)))
        infile.close()
        
    def printTria3(self):
        for p in self.tria_p:
            print p
        
    def printQuad4(self):
        for p in self.quad_p:
            print p
                
    def printNsided(self):
        for p in self.nsided_p:
            print p



#---function---
def readSurfaceFile(fileName):
    surf= []
    surfFile = open(fileName, 'r')
    for s in surfFile:
        surf.append(s.strip())
    surfFile.close()
    return surf
    
def readTimeData(fileName):
    tim = []
    timeFile = open(fileName, 'r')
    for t in timeFile:
        tim.append(t.strip())
    timeFile.close()
    return tim

def getScalData(inGeoDir, inFileDir, tim, surf, rho):
    sc = []
    for t in tim:
        inGeoFileName = os.path.join(inGeoDir, surf+".geo")
        infileName = os.path.join(inFileDir, t)
        infileName = os.path.join(infileName, surf+"_p")
        print "geo file:  " + inGeoFileName
        print "scal file: " + infileName
        p = Pressure(inGeoFileName, infileName, rho, t)
        p.readGeo()
        p.readP()
        sc.append(p)
    return sc

def writeTimesPdata(outDir, surf, scalar):
    fileName = os.path.join(outDir, surf + '.dat')
    outFile = open(fileName, 'w')
    sp = " "
    num = 0
    for scal in scalar:        
        tria = scal.getTria3()
        quad = scal.getQuad4()
        nside = scal.getNsided()
        if num == 0:
            num = int(tria) + int(quad) + int(nside)
        outFile.write(str(scal.t) + sp)
        if tria > 0:
            for p in scal.getTriaP():
                outFile.write(str('{0:12.5e}'.format(p))+sp)
        if quad > 0:
            for p in scal.getQuadP():
                outFile.write(str('{0:12.5e}'.format(p))+sp)
        if nside > 0:
            for p in scal.getNsidedP():
                outFile.write(str('{0:12.5e}'.format(p))+sp)
        outFile.write("\n")  
    outFile.close()
    print "write file: " + fileName
    return num
    
def writeLookUp(outDir, t, surf):  
    lookupFileName = os.path.join(outDir, "SPL.lookup")
    lookupFile = open(lookupFileName, 'w')
    for s in surf:
        inGeoFileName = os.path.join(inGeoDir, s+".geo")
        print "geo file:  " + inGeoFileName
        p = Pressure(inGeoFileName, "dummy", rho, t)
        p.readGeo()
        tria = p.getTria3()
        quad = p.getQuad4()
        nside = p.getNsided()
        lookupFile.write(s + " " + str(tria) + " " + str(quad) + " "+ str(nside) + "\n")        
    lookupFile.close()   

#--- main ---
homeDir = '/home2/tshimizu/ES/MMC_AERO/case4'
inGeoDir = os.path.join(homeDir, 'GEOM_ascii')
inFileDir = os.path.join(homeDir, 'surface')
outFileDir = os.path.join(homeDir, 'Parts')

rho = 1.205

surfFileName = os.path.join(homeDir, 'surf_list.dat')
surfaces = readSurfaceFile(surfFileName)

timeFileName = os.path.join(homeDir, 'time.dat')
times = readTimeData(timeFileName)

writeLookUp(outFileDir, times[0], surfaces)


for s in surfaces:
    times_p = getScalData(inGeoDir, inFileDir, times, s, rho)
    num = writeTimesPdata(outFileDir, s, times_p)



if __name__ == '__main__':
    pass