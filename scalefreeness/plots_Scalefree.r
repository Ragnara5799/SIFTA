draft = F
#if (draft) dev.off()

library("igraph")

options(width=180)

#ca=commandArgs(trailingOnly=TRUE) #only args after --args

#interpret all elements of ca as names of case studies

#http://www.cookbook-r.com/Graphs/Multiple_graphs_on_one_page_%28ggplot2%29/
# Multiple plot function
#
# ggplot objects can be passed in ..., or to plotlist (as a list of ggplot objects)
# - cols:   Number of columns in layout
# - layout: A matrix specifying the layout. If present, 'cols' is ignored.
#
# If the layout is something like matrix(c(1,2,3,3), nrow=2, byrow=TRUE),
# then plot 1 will go in the upper left, 2 will go in the upper right, and
# 3 will go all the way across the bottom.
#
multiplot <- function(..., plotlist=NULL, file, cols=1, layout=NULL) {
  library(grid)

  # Make a list from the ... arguments and plotlist
  plots <- c(list(...), plotlist)

  numPlots = length(plots)

  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                    ncol = cols, nrow = ceiling(numPlots/cols))
  }

 if (numPlots==1) {
    print(plots[[1]])

  } else {
    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))

    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))

      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
                                      layout.pos.col = matchidx$col))
    }
  }
}

countFeatures <- function(featureCondition) {
	#replace everything but the space chars with "", and count the remaining (space-) chars
	nchar(gsub("[^ ]","",featureCondition)) + 1
}
filterLowInfluence <-function(datatable, threshold=50) { #take only the threshold% most influencial interactions (absolute values count)
	len = nrow(datatable)
	sortedDescending = datatable[order(-abs(datatable$influence)),]
	toTake=len*threshold/100
	head(sortedDescending, toTake)
}
drop_0Degree_Interactions <-function(datatable) { #remove all interactions of degree 0
	datatable[datatable$interactionDegree>0,]
}
minmaxseq<-function(..., vec=c()) {
	c(min(c(c(...),vec)):max(c(c(...),vec)))
}
dropNonIntNumbers <-function(vec=c()) {
	isInt <-function(x) {x%%1==0}
	Filter(isInt, vec)
}
#print(csvData)
#rgb(red, green, blue, alpha, names = NULL, maxColorValue = 1)
#color <- c(rgb(1, 0, 0), rgb(0, 0, 1), rgb(.35, .35, .35)) # setup, typecheck, bytecodeComp
#solarize colors
solarizeColors <- c(
	rgb(133, 153,   0, maxColorValue = 255),  #{sol_green}  
	rgb( 38, 139, 210, maxColorValue = 255),  #{sol_blue}   
	rgb(181, 137,   0, maxColorValue = 255),  #{sol_yellow} 
	rgb(108, 113, 196, maxColorValue = 255),  #{sol_violet} 
	rgb(203,  75,  22, maxColorValue = 255),  #{sol_orange} 
	rgb(211,  54, 130, maxColorValue = 255),  #{sol_magenta}
	rgb(255, 255, 255, maxColorValue = 255),  #{white}
	rgb(220,  50,  47, maxColorValue = 255),  #{sol_red}    
	rgb( 42, 161, 152, maxColorValue = 255)  #{sol_cyan}  
)


print(" scalefreeness for Nodes (intents)")

#qplot(numFeatures,numFeatures,data=csvdata)

studyFile = c("../degree_histogram.txt")
dataframe <- read.csv(file=studyFile,head=TRUE, sep="\t", na.strings=c("","NA"))
spread=c()
for(i in 1:nrow(dataframe)) {
    row <- dataframe[i,]
    spread = c(spread,rep(row$Degree, row$Frequency))
}
#exponential.model <- lm(log(Frequency)~ Degree, data = dataframe)
#exponential.model <- nls(Degree ~ exp(a+b*Frequency), data=dataframe, start=list(a=0,b=0))
#summary(exponential.model)
fit <- power.law.fit(spread, implementation="plfit")
#print(spread)
print(fit)

pdf(file = paste("expfit_Intent_degree.pdf",sep=""), width= 30, height = 30, useDingbats=F)
fitData <- data.frame(Degree = seq(0, max(dataframe$Degree), 1))
max=max(dataframe$Frequency)
b=dataframe[dataframe$Degree==1,]$Frequency
fitData$Frequency <- b*(fitData$Degree^-fit$alpha)  #exp(predict(exponential.model,fitData))
cat(paste("fit function: ", b, "*x^-", fit$alpha,"\n", sep=""))
plot(dataframe$Degree, dataframe$Frequency,pch=16, log="xy")
lines(fitData$Degree,fitData$Frequency,lwd=2, col = "red", xlab = "Degree", ylab = "Frequency")
#lines(x^fit$alpha,lwd=2, col = "red", xlab = "Degree", ylab = "Frequency")

	#pdf(file = paste("Svens_einzelne_plots/plots_Sven_ALL",csname,".pdf",sep=""), width= 50, height = 10, useDingbats=F)
	#multiplot(cols=length(plotlist)/2, plotlist=plotlist)

    #+ geom_jitter(aes(size=.05, col=industry),position=position_dodge(width = 0.8))


print(" scalefreeness for Apps (\"Edges\")")

studyFile = c("./AppNodeDegreeCount.csv")
dataframe <- read.csv(file=studyFile,head=TRUE, sep=",", na.strings=c("","NA"))
spread=c()
for(i in 1:nrow(dataframe)) {
    row <- dataframe[i,]
    spread = c(spread,rep(row$Degree, row$Count))
}
#exponential.model <- lm(log(Frequency)~ Degree, data = dataframe)
#exponential.model <- nls(Degree ~ exp(a+b*Frequency), data=dataframe, start=list(a=0,b=0))
#summary(exponential.model)
fit <- power.law.fit(spread, implementation="plfit")
#print(spread)
print(fit)

pdf(file = paste("expfit_App_degree.pdf",sep=""), width= 30, height = 30, useDingbats=F)
fitData <- data.frame(Degree = seq(0, max(dataframe$Degree), 1))
max=max(dataframe$Count)
b= dataframe[dataframe$Degree==1,]$Count
fitData$Count <- b*(fitData$Degree^-fit$alpha)  #exp(predict(exponential.model,fitData))
cat(paste("fit function: ", b, "*x^-", fit$alpha,"\n", sep=""))
plot(dataframe$Degree, dataframe$Count,pch=16, log="xy")
lines(fitData$Degree,fitData$Count,lwd=2, col = "red", xlab = "Degree", ylab = "Frequency")


warnings()
#if (!draft) dev.off()

