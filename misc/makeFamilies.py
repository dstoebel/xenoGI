import sys,os
sys.path.append(os.path.join(sys.path[0],'..'))
import parameters,genbank,trees,genomes,scores,families,islands

## Does family making without island making (i.e. the first half of
## what xenoGI.py does).

if __name__ == "__main__":

    paramFN=sys.argv[1]
    paramD = parameters.loadParametersD(paramFN)

    ## load data structures we'll use below
    tree,strainStr2NumD,strainNum2StrD = trees.readTree(paramD['treeFN'])

    # an object for gene name conversions
    geneNames = genomes.geneNames(paramD['geneOrderFN'],strainStr2NumD,strainNum2StrD)

    subtreeL=trees.createSubtreeL(tree)
    subtreeL.sort()
    geneOrderT=genomes.createGeneOrderTs(paramD['geneOrderFN'],geneNames,subtreeL,strainStr2NumD)

    ## read scores
    scoresO = scores.readScores(paramD['scoresFN'],geneNames)

    ## make gene families
    outputSummaryF = open(paramD['outputSummaryFN'],'w')
    familyL = families.families(tree,subtreeL,geneNames,scoresO,paramD['minNormThresh'],paramD['minCoreSynThresh'],paramD['minSynThresh'],paramD['synAdjustThresh'],paramD['synAdjustExtent'],paramD['familyFN'],strainNum2StrD,outputSummaryF)
    outputSummaryF.close()
