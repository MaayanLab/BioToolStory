#################################################################
#################################################################
############### Bioinformatics Tools R Support Functions ########
#################################################################
#################################################################
##### Author: Megan Wojciechowicz
##### Affiliation: Ma'ayan Laboratory,
##### Icahn School of Medicine at Mount Sinai

#############################################
########## 1. Load libraries
#############################################
##### 1. R modules #####
library("ggplot2")
library("tibble")
library("Rtsne")
library("plotly")
library("htmlwidgets")
#################################################################
#################################################################
############### 1. Support Functions ############################
#################################################################
#################################################################

#######################################################
#######################################################
########## S1. Exploratory Data Analysis
#######################################################
#######################################################

#############################################
########## 1. t-SNE
#############################################

run_tsne <- function(infile, outfile, dims, color_by, outfile3D, remove_na){
    
    print('Building Matrix........')
    
    # read in similarity matrix
    df<-read.csv(infile[[1]], stringsAsFactors = FALSE, row.names = 1, header=TRUE, sep=',')
    
    # read tool info 
    df_info <- read.csv(infile[[2]], header=TRUE,stringsAsFactors = FALSE, sep = '\t')
    
    # remove na's if necessary
    if (remove_na != ''){
         df_info <- df_info[!is.na(df_info[[remove_na]]),]
    }

    # create matrix 
    data<-as.matrix(df)
    
    # fill diagonal with 0
    data[is.na(data)] <- 0

    print('Running t-SNE........')

    # run t-SNE
    tsne<- Rtsne(data, dims=3, perplexity=10, check_duplicates = FALSE)
    
    print('Finished t-SNE.....')

    tsne2<-as.data.frame(tsne$Y)

    tsne2$pub_year <- df_info$pub_year
    
    tsne2$journal_name <- df_info$journal_name

    tsne2$tool_name <- df_info$tool_name

    tsne2$doi <- df_info$doi

    write.csv(tsne2, file = outfile, sep=",")

    # all_files <- 0

    # for (category in color_by){
        
    #     # plot all t-SNE dimensions in 2D and color by age and journal name 
    #     index = 0 

    #     print('Plotting t-SNE........')
        
    #     colors <- topo.colors(length(unique(tsne[[category]])))
        
    #     names(colors) = unique(tsne[[category]])
        
    #     for (dim in dims){

    #         print('*********************')
    #         print(dim[[1]][1])
    #         print(dim[[2]][1])
    #         print('*********************')

    #         index <- index + 1

    #         all_files <- all_files +1
    #         #print(par('mar'))
    #         #par(mar=c("bottom" = 5, "left" = 5, "top" = 4, "right" = 5))
    #         #setEPS()
    #         #print('making.....')
    #         #print(outfile[all_files])
    #         #quartz()
            
    #         #postscript(outfile[all_files],paper="special",horizontal=F,onefile=F)
    #         #X11 ()
         
    #         #dev.copy(postscript, filename=outfile[[all_files]][1])
    #         #postscript(file =outfile[all_files],paper="special",horizontal=F,onefile=F)
    #         print(outfile[all_files])
    #         # setEPS()

    #         # postscript(file =outfile[all_files], horiz=FALSE,onefile=FALSE,paper='letter')
            
    #         # plot(tsne$Y[,dim[[1]][1]],tsne$Y[,dim[[2]][1]],col=colors,pch = 20,cex = 0.75,cex.axis = 1.25, cex.lab = 1.25, cex.main = 1)
            
    #         # legend('topright',legend=unique(tsne[[category]]),col=colors, pch=20,inset=c(-0.15,0),xpd=TRUE)

    #         # dev.off()
    #         cairo_ps(outfile[all_files])
    #         plot(tsne$Y[,dim[[1]][1]],tsne$Y[,dim[[2]][1]],col=colors,pch = 20,cex = 0.75,cex.axis = 1.25, cex.lab = 1.25, cex.main = 1)
    #         #legend('topright',legend=unique(tsne[[category]]),col=colors, pch=20,inset=c(-0.15,0),xpd=TRUE)
    #         dev.off()



    #    }
    # }

    # plot 3D t-SNE
    for (category in color_by){

        dimensions<- as.data.frame(tsne$Y)
        
        dimensions$pub_year <- df_info$pub_year
        
        dimensions$pub_year<-as.factor(dimensions$pub_year)

        dimensions$journal_name <- df_info$journal_name

        dimensions$tool_name <- df_info$tool_name

        colnames(dimensions)=c("tsne$Y[,1]","tsne$Y[,2]","tsne$Y[,3]","pub_year","journal_name" ,"tool_name")

        colors <- topo.colors(length(unique(dimensions[[category]])))
        
        p <- plot_ly(dimensions, x=tsne$Y[,1], y=tsne$Y[,2], z=tsne$Y[,3], color= dimensions[[category]], colors=colors, text=dimensions$tool_name, hoverinfo= "text+x+y+z",type="scatter3d", mode="markers")
        
        saveWidget(p, file=paste(outfile3D,category,".html" ,sep=''), selfcontained=TRUE)
    }
    print('DONE!')
}

run_tsne_topics<- function(data){
    
    print('Running t-SNE........')

    # run t-SNE
    tsne<- Rtsne(data, dims=3, perplexity=10, check_duplicates = FALSE)

    print('Finished t-SNE.....')

    tsne2<-as.data.frame(tsne$Y)
    
    return(tsne2)
}
