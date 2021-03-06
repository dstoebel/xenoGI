## This parameter file contains python expressions with info on files
## and parameters

#### Input file parameters ####

# Tree file in newick format. This should have named internal
# nodes. It does not need to have branch lengths (if it has them, they
# will be ignored).
treeFN='example.tre'

# The node and the branch leading to it define the focal clade where
# islands will be reconstructed. Everything outside of this will be
# treated as ougroups (e.g. won't merge islands there).
rootFocalClade = 'i0'

# unix style file path to genbank gbff files
genbankFilePath = 'ncbi/*.gbff'

#### Parse output files ####

# gene order
geneOrderFN = 'geneOrder.txt'

# list of protein names found to be redundant in genbank files (will not
# be used)
redundProtsFN = 'redundProts.txt'

# gene descriptions (for use in analysis)
geneInfoFN = 'geneInfo.txt'

# A file specifying the mapping between genbank file names and human
# readable names. These human readable names are then used to to refer
# to the various species in subsequent analysis. They should match
# what's in the tree. If we don't want to rename and will use NCBI
# file names in later analysis, set to None.
fileNameMapFN = 'ncbiHumanMap.txt'

# unix style file path to fasta files
fastaFilePath = 'fasta/*.fa'


#### Blast output ####

# absolute path to the directory containing the blastp and makeblastdb executables. Write this in whatever style is typical for the machine you are on, e.g. if it is windows, then using windows style \ etc.
blastExecutDirPath = '/usr/bin/'

# blast command line (except for db,query and outfiles)
blastCLine = 'blastp -matrix BLOSUM62 -gapopen 11 -gapextend 1 -evalue 0.01 -seg yes -outfmt 6'

# unix style file path to blast output files
blastFilePath = 'blast/*.out'


#### Algorithm output files ####

# Note: for scores output files, if the extension we use here is
# .bout, the output will be saved in binary format (a pickle of a
# networkx graph). Otherwise it will be a less compact text based
# format

scoresFN = 'scores.bout'

# sets of all around best reciprocal hits
aabrhFN = 'aabrh.out'

# family file
familyFN='fam.out'

# island file
islandOutFN = 'islands.out'

# file with summary info about family and island formation
familyIslandFormationSummaryFN = 'familyIslandFormationSummary.out'

#### Algorithm parameters ####

# in parallel code, how many threads to use
numThreads = 50

# in calculation of normalized scores, we get set of all around best
# reciprocal hits. This is the evalue threshold used there.
evalueThresh = 0.001

# alignment parameters for making scores
# note, since parasail doesn't charge extend on the first base its
# like emboss, and not like ncbi blast. NCBI blast uses existance 11,
# extend 1 for blosum 62, thus we should use open 12 gapExtend 1 here.
gapOpen = 12
gapExtend = 1
matrix = 'parasail.blosum62'

# Synteny window size, that is the size of the neighborhood of each
# gene to consider when calculating synteny scores. (measured in
# number of genes). We go half this distance in either direction.
synWSize = 8

# When calculating synteny score between two genes, the number of
# pairs of scores to take (and average) from the neighborhoods of
# those two genes
numSynToTake = 3

# Core synteny window size, that is the number of core genes from the
# neighborhood of each gene to consider when calculating core synteny
# scores. (measured in number of genes). We go half this distance in
# each direction.
coreSynWsize = 20

# Threshold for the core gene synteny score required for family
# formation. (These scores range from 0 to 1). Note that if this is
# set to higher than 0.5, then there will need to be at least one core
# gene on both sides. This would mean that things at the end of a
# contig won't get added to families because they lack a common core
# gene on that side.
minCoreSynThresh = 0.5

# Minimum normalized score for family formation. This should be used
# as an extreme lower bound, to eliminate those things that are so
# obiously dissimilar that they could not be homologous by descent
# from the node under consideration. In units of standard deviation,
# centered around 0.
minNormThresh = -11.0

# Minimum synteny score value we'll accept when putting a gene in a
# family. Also applies to seeds. Note synteny scores are based on
# normalized scores
minSynThresh = -4.0

# Synteny score threshold for using synteny to adjust a raw
# score. Setting this lower makes us use synteny more, and thus will
# tend to make us put more genes in families. This is a normScore type
# score
synAdjustThresh = -2

# We use syntenty scores to adjust similarity scores in family
# finding. This parameter specifies the amount we multiply a rawScore
# by during this adjustment.
synAdjustExtent = 1.05

# In deciding whether to merge two islands, we judge partly based on
# the proximity of their genes. The elements of this list are tuples
# of the form (proximity threshold, rscore level). For example (1,0)
# says we'll consider proximity to mean adjacency (proximity 1 means
# adjacent genes), and we'll join islands if the rscore values is 0 or
# above. The algorithm loops through the list, using the criteria in
# the first tuple first, then proceeding to the second if there is on
# and so on.
proxThreshL = [(1,0),(2,2)]


#### Visualization and analysis ####

# We count possible errors in a family. This dictionary specifies the
# increments with which we identify near misses in adding families to
# genes. If adding or subtracting this amount to a gene's score
# changes our choice about whether to add it, then we have a near
# miss, and will count it in our possible error count for the family.
famErrorScoreIncrementD = {'normSc':1.0, 'synSc':1.0, 'coreSynSc':0.1}

# Creating gff files of islands for visualization in the IGB browser.
# We want to display different islands with different colors. We do
# this by giving different 'score' values to different islands. Scores
# can range from 1 to 1000, but we only give certain discrete scores.

scoreNodeMapD = {'i1':1,'i2':6} # islands with these mrca values always get this score

# The score for rest is based on the list below. It was made with
# createIslandGffs.createPotentialScoresL(100,1001,200,50)
potentialScoresL=[100, 300, 500, 700, 900, 150, 350, 550, 750, 950, 200, 400, 600, 800, 1000, 250, 450, 650, 850]

# The possible rgb values for bed files is based on the list below. 
potentialRgbL = ['245,130,48', '188,143,14','0,102,0','230,26,135','0,0,128', '145,30,180','0,255,255','128,0,0','0,255,0', '255,0,255','240,230,140','32,178,170','240,128,128','255,0,0','100,149,237','60,179,113','0,255,130','128,128,128','94,94,94','102,51,0']

#### Visualization and analysis output files ####

# unix style file path to bed, gff output files
bedFilePath = 'bed/*-island.bed'
gffFilePath = 'gff/*-island.gff'

islandsSummaryFN = 'islandsSummary.out'

genesFNstem = 'genes'
genesFNextension = '.out'
