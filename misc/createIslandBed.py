import sys,statistics,os,glob
from urllib import parse
sys.path.append(os.path.join(sys.path[0],'..'))
import trees, genomes, families, islands, parameters, random


def createIslandByStrainD(leafNodesL,strainNum2StrD,islandByNodeL,familyL,geneNames,geneInfoD):
    '''Return a dict keyed by strain name. Values are lists of tuples
    (islandNum, familyL) where familyL is a list of tuples in the island
    present in that strain. Family tuples are (family,[genes in
    family]).
    '''
    islandByStrainD = {}
    for leaf in leafNodesL:
        islandByStrainD[strainNum2StrD[leaf]]=[]

    # loop over every node in tree. examine each island. from each
    # extract the genes present in each strain and put in right entry
    # in islandByStrainD
    for mrcaNum in range(len(islandByNodeL)):
        for gr in islandByNodeL[mrcaNum]:

            # make dict to collect fams for each strain
            tempStrainD = {}
            for leaf in leafNodesL:
                tempStrainD[strainNum2StrD[leaf]]=[]

            for fam in gr.familyL:

                # famGeneT is a tuple, where index is strain
                # number. It only has non zero entries at
                # tips. Located at each index is a tuple of gene (gene
                # count, (tuple of genes)). We access by looping over
                # leaf nodes
                fgT = familyL[fam].famGeneT

                for leaf in leafNodesL:
                    geneT = fgT[leaf]

                    # if the family has a gene or genes in this
                    # strain, add tuple (family,[genes in family]) to
                    # list for this strain
                    if len(geneT) > 0:
                        geneNamesL=[geneNames.numToName(gene) for gene in geneT]
                        tempStrainD[strainNum2StrD[leaf]].append((fam,geneNamesL))


            # now make island tuple (minStart,island, familyL) where
            # minStart is the lowest start coord we've seen in the
            # island, island is the island id, and familyL is the thing
            # in tempStrainD
            for strain in islandByStrainD:
                # only add if the island is present in this strain

                if tempStrainD[strain] != []:
                    #print(gr.id,mrcaNum,strain)
                    chrom,islandMedianMidpoint,islandMin,islandMax = getIslandPositions(tempStrainD[strain],geneInfoD,strainNum2StrD,gr.id,mrcaNum,strain)
                    grT = (chrom,islandMedianMidpoint,islandMin,islandMax,mrcaNum,gr.id,tempStrainD[strain])
                    islandByStrainD[strain].append(grT)
                    
    # sort each list in islandByStrainD by chrom and islandMedianMidpoint
    for strain in islandByStrainD:
        islandByStrainD[strain].sort(key=lambda x: x[:2])
    
    return islandByStrainD

def getIslandPositions(familyL,geneInfoD,strainNum2StrD,grID,mrcaNum,strain):
    '''Given a list of families (from a single island in a single strain),
return its chrom,start,end.
    '''
    chromL=[]
    islandMin=float('inf')
    islandMax=-float('inf')
    geneMidpointL=[]
    for fam,geneL in familyL:
        for gene in geneL:
            commonName,locusTag,descrip,chrom,start,end,strand=geneInfoD[gene]
            chromL.append(chrom)
            start = int(start)
            end = int(end)
            if start<islandMin:
                islandMin=start
            if end>islandMax:
                islandMax=end

            geneMidpointL.append(int((end-start)/2))
                
    # sanity check: all entries in chromL should be same
    if not all((c==chromL[0] for c in chromL)):
        print("Genes in island",grID,"at mrca",strainNum2StrD[mrcaNum],"in strain",strain,"are not all on the same chromosome.",file=sys.stderr)

    islandMedianMidpoint = statistics.median(geneMidpointL)
    
    return chrom,islandMedianMidpoint,islandMin,islandMax

def orderedIslandsInStrain(strainName):
    '''returns a list of all the islands in the strain given, in the order they appear'''
    islandsInStrainL = islandByStrainD[strainName]
    chromStartIslandLL = []
    #for each island in the strain, order first by chromosome and then by island start pos
    for islandT in islandsInStrainL:
        chrom,_,start,_,_,islandNum,familyL=islandT
        chromStartIslandLL.append([chrom,start,islandT])
    sortedChromStartIslandLL = sorted(chromStartIslandLL)
    #make an ordered list of just the islands without the other information
    sortedIslandsL = [x[2] for x in sortedChromStartIslandLL]
    return sortedIslandsL


def islandToBed(islandT,geneInfoD,tree,strainNum2StrD,scoreNodeMapD, islandColorD):
    '''Given a islandT (the values of islandByStrainD are lists of these)
convert into a string suitable for writing in a bed file. Return
this. Note that we're using the score field to color the genes in
IGB. So, we give genes in a island the same score, and give different
scores to adjacent islands. Counter keeps track of how many islands
we've done already.
    '''
    bedL=[]
    chrom,islandMedianMidpoint,islandMin,islandMax,mrcaNum,grNum,familyL = islandT
    islandID = 'island_'+str(grNum)
    score = str(islandColorD[str(grNum)])
    
    # loop over families to get genes
    for fam,geneL in familyL:
        for gene in geneL:
            commonName,locusTag,descrip,chrom,start,end,strand=geneInfoD[gene]
            if commonName != '':
                Name=commonName
            else:
                Name=gene

            attributes = 'ID='+gene+';Name='+Name+';gene='+Name+';Note= | '+islandID+" | fam_"+str(fam)+" | mrca_"+strainNum2StrD[mrcaNum] + " | "+descrip
            
            bedL.append('\t'.join([chrom,start,end,Name,'0',str(strand),start,start,score,'1',str(int(end)-int(start)),'0',gene,attributes]))

    bedStr = '\n'.join(bedL)
    return bedStr
    
def writeStrainBed(islandByStrainD,geneInfoD,tree,strainNum2StrD,strain,bedFileName,scoreNodeMapD,islandColorD):
    '''For a given strain, Write bed file.'''
    f=open(bedFileName,'w')
    f.write('track name='+strain+' type=bedDetail visibility=full itemRgb="On" useScore=0 \n')
    orderedIslandsInStrainL = orderedIslandsInStrain(strain)
    for islandT in orderedIslandsInStrainL:
        bedStr = islandToBed(islandT,geneInfoD,tree,strainNum2StrD,scoreNodeMapD,islandColorD)
        f.write(bedStr+'\n')
    f.close()

def createAllBeds(islandByStrainD,geneInfoD,tree,strainNum2StrD,bedFilePath,scoreNodeMapD,potentialRgbL):

    # if directory for beds doesn't exist yet, make it
    bedDir = bedFilePath.split("*")[0]
    if glob.glob(bedDir)==[]:
        os.mkdir(bedDir)

    bedExtension = bedFilePath.split("*")[1]
    minIslandsMiscolored = 1000
    strainL = list(islandByStrainD.keys())
    for i in range(0,numTries):
        random.shuffle(strainL)
        numberOfIslandsMiscolored,islandColorD  = createIslandColorD(strainL,scoreNodeMapD,strainNum2StrD,potentialRgbL)
        if numberOfIslandsMiscolored<minIslandsMiscolored:
            bestColorD = islandColorD
            minIslandsMiscolored = numberOfIslandsMiscolored
    islandColorD = bestColorD
    numberOfIslandsMiscolored = minIslandsMiscolored
    
    for strain in islandByStrainD:
        bedFileName = bedDir+strain+bedExtension
        writeStrainBed(islandByStrainD,geneInfoD,tree,strainNum2StrD,strain,bedFileName,scoreNodeMapD,islandColorD)

    print('Number of islands miscolored is '+str(numberOfIslandsMiscolored)+' after '+str(numTries)+' tries.',file=sys.stderr)


def islandsNextToSameColorCount(islandByStrainD,islandColorD,scoreNodeMapD):
    '''counts the number of islands that are adjacent to the same color island'''
    miscolorCount = 0
    for strain in islandByStrainD:
        orderedIslandsInStrainL = orderedIslandsInStrain(strain)
        for islandIndex in range(1,len(orderedIslandsInStrainL)):
            mrcaNum = orderedIslandsInStrainL[islandIndex-1][-3]
            if strainNum2StrD[mrcaNum] not in scoreNodeMapD:
                if islandColorD[str(orderedIslandsInStrainL[islandIndex][-2])] is islandColorD[str(orderedIslandsInStrainL[islandIndex-1][-2])]: miscolorCount+=1
                   
    return miscolorCount

def createIslandColorD(strainL,scoreNodeMapD,strainNum2StrD,potentialRgbL):
    '''make the island color dictionary'''
    islandColorD = {}
    for strain in strainL:
        counter = 0
        orderedIslandsInStrainL = orderedIslandsInStrain(strain)
        for islandIndex in range(0,len(orderedIslandsInStrainL)):
            island = orderedIslandsInStrainL[islandIndex]
            #make a variable holding the previous island to compare colors
            if islandIndex != 0:
                prevIsland = orderedIslandsInStrainL[islandIndex-1]
                prevIslandNum = str(prevIsland[-2])
            mrcaNum = island[-3]
            islandNum= str(island[-2])

            # create score for coloring islands
            if strainNum2StrD[mrcaNum] in scoreNodeMapD:
                score = '0,0,0'
                islandColorD[islandNum]=str(score)
            elif str(islandNum) in islandColorD:
                score = str(islandColorD[str(islandNum)])
            else:
                score = str(potentialRgbL[counter%len(potentialRgbL)])
                islandColorD[islandNum]=str(score)
                counter += 1

            #for all islands except the first one, see if the previous island is the same
            #color. if so, pick the next color and increment the counter
            if (islandIndex != 0) and (strainNum2StrD[mrcaNum] not in scoreNodeMapD):
                if islandColorD[islandNum] is islandColorD[prevIslandNum]:
                    score = str(potentialRgbL[counter%len(potentialRgbL)])
                    islandColorD[islandNum]=str(score)
                    counter += 1

    numberOfIslandsMiscolored = islandsNextToSameColorCount(islandByStrainD,islandColorD,scoreNodeMapD)

    return numberOfIslandsMiscolored, islandColorD
        
if __name__ == "__main__":

    paramFN=sys.argv[1]
    numTries = int(sys.argv[2])
    paramD = parameters.loadParametersD(paramFN)

    ## load data structures we'll use below
    tree,strainStr2NumD,strainNum2StrD = trees.readTree(paramD['treeFN'])
    leafNodesL = trees.leafList(tree)
    geneNames = genomes.geneNames(paramD['geneOrderFN'],strainStr2NumD,strainNum2StrD)
    familyL = families.readFamilies(paramD['familyFN'],tree,geneNames,strainStr2NumD)
    islandByNodeL=islands.readIslands(paramD['islandOutFN'],tree,strainStr2NumD)
    geneInfoD = genomes.readGeneInfoD(paramD['geneInfoFN'])    

    
    # get islands organized by strain
    islandByStrainD = createIslandByStrainD(leafNodesL,strainNum2StrD,islandByNodeL,familyL,geneNames,geneInfoD)

    createAllBeds(islandByStrainD,geneInfoD,tree,strainNum2StrD,paramD['bedFilePath'],paramD['scoreNodeMapD'],paramD['potentialRgbL'])
