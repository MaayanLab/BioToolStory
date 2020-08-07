library('sqldf')
library('ggplot2')
library('readxl')
library('dotenv')
library('ggfortify')

load_dot_env(file = paste0(getwd(),"PubMedTools/CF/.env"))
PTH = Sys.getenv("PTH")

tools <- read_excel(paste0(PTH,'data/tools_new.xlsx'),skip=1)

a<-c("Journal_Issue_PubDate_Year",
     "CF_program",
     "Institution",
     "PMID",
     "Project_Number",
     "Tool_Name",
     "Citations",
     "Added_On",                                         
    "Date_Completed_Year",
    "ISSN",
    "Journal_ISO_Abbreviation",
    "Readers_Count",
    "Cited_By_Posts_Count",
    "Twitter accounts that tweeted this publication",
    "Users who've mentioned the publication on Twitter",
    "Mentions in social media","Altmetric_Score"
    )

tools1<-tools[,a]

# --------------------- pi charts of tools per journal -------------------------------------------------------------------------------------------------------------------------
theme_set(theme_bw())
df<-sqldf("select Journal_ISO_Abbreviation, count(1) as tools from tools group by Journal_ISO_Abbreviation order by tools DESC LIMIT 10")
df<-df[!is.na(df$tools),]
df$tools<-factor(df$tools)
colnames(df) <- c("Journal", "freq")

df$Journal <- factor(df$Journal, levels = df$Journal)

pie <- ggplot(df, aes(x =freq, y=freq, fill = factor(Journal))) + 
  geom_bar(width = 1, stat = "identity") +
  theme(axis.line = element_blank(), 
        plot.title = element_text(hjust=0)) +
  labs(fill="Journal", 
       subtitle="2009 - 2019", 
       x=NULL, 
       y=NULL, 
       title="Top 10 journals for tools publications")
pie + coord_polar(theta = "x", start=0)


# --------------------- bar chart tools per year ------------------------------------------------------------------------------------------------------------

ty<-sqldf("select Date_Completed_Year, count(1) as tools from tools where Date_Completed_Year< 2020 group by Date_Completed_Year")
ty$Date_Completed_Year<-as.character(ty$Date_Completed_Year)

# Barplot
g <- ggplot(ty, aes(ty$Date_Completed_Year, ty$tools))
g + geom_bar(stat="identity", width = 0.5, fill="tomato2") + 
  labs(title="Tools per year", 
       subtitle="2009 - 2019", 
       y="Tools",
       x="Year") +
  theme(axis.text.x = element_text(angle=65, vjust=0.6))

# --------------------- stacked bar chart citations per tool -------------------------------------------------------------------------------------------------------------------------

# select the top 50 tools with the most citations
t1<-sqldf("select Tool_Name, sum(citations) as tools from tools1 group by Tool_Name order by tools DESC LIMIT 50")
t2<-sqldf("select Tool_Name, sum(Cited_By_Posts_Count) as tools from tools1 group by Tool_Name order by tools DESC")
t2<-t2[t2$Tool_Name %in% t1$Tool_Name,]
t4<-sqldf("select Tool_Name, sum(`Twitter accounts that tweeted this publication`) as tools from tools1 group by Tool_Name order by tools DESC")
t4<-t4[t4$Tool_Name %in% t1$Tool_Name,]
t5<-sqldf("select Tool_Name, sum(`Mentions in social media`) as tools from tools1 group by Tool_Name order by tools DESC")
t5<-t5[t5$Tool_Name %in% t1$Tool_Name,]
t6<-sqldf("select Tool_Name, sum(Readers_Count) as tools from tools1 group by Tool_Name order by tools DESC")
t6<-t6[t6$Tool_Name %in% t1$Tool_Name,]
t7<-sqldf("select Tool_Name, sum(`Users who've mentioned the publication on Twitter`) as tools from tools1 group by Tool_Name order by tools DESC")
t7<-t7[t7$Tool_Name %in% t1$Tool_Name,]

t1$cond<-'Citations'
t2$cond<-'Social media Posts'
t4$cond<-'Tweeting users'
t5$cond<-'Social media mentions'
t6$cond<-'Social media Readers'
t7$cond<-'Twitter mentions'

names(t1)<-c("Tool_name","value","Citation")
names(t2)<-c("Tool_name","value","Citation")
names(t4)<-c("Tool_name","value","Citation")
names(t5)<-c("Tool_name","value","Citation")
names(t6)<-c("Tool_name","value","Citation")
names(t7)<-c("Tool_name","value","Citation")

tall<-rbind(t1,t2,t4,t5,t6,t7)
tall$Citation<-as.factor(tall$Citation)
tall[is.na(tall)] <- 0
rm(t1,t2,t4,t5,t6,t7)

# Stacked
ggplot(tall, aes(fill=Citation, y=value, x=reorder(Tool_name,value,sum))) + 
  geom_bar(position="stack", stat="identity") +
  labs(title="Top 50 cited tools", 
       x = "Tool name",
       y = "Citations",
       subtitle="2009 - 2019") + 
  theme(axis.text.x = element_text(angle=90, vjust=0.2, hjust=0.95))


# --------------------- tools per CF program -------------------------------------------------------------------------------------------------------------------------
n<-c(
  '4D Nucleome',
  'Genotype-Tissue Expression (GTEx)',
  'The Human BioMolecular Atlas Program',#** In future programs
  'Gabriella Miller Kids First',
  'Library of Integrated Network-Based Cellular Signatures (LINCS)',
  'Metabolomics',
  'Molecular Transducers of Physical Activity in Humans',
  'Stimulating Peripheral Activity to Relieve Conditions (SPARC)',
  'Undiagnosed Diseases',
  'Illuminating the Druggable Genome',
  'Acute to Chronic Pain Signatures (A2CPS)',#** There are no funding opportunities at this time
  'Extracellular RNA Communication',
  'Knockout Mouse Phenotyping',
  'Human Microbiome Project')

short<- c('4D Nucleome',
          'GTEx',
          'HuBMAP',
          'Kids First',
          'LINCS',
          'Metabolomics',
          'MoTrPAC',
          'SPARC',
          'UDN',
          'IDG',
          'A2CPS',
          'ExRNA',
          'KOMP',
          'HMP')

df = data.frame(n,short)
df$short<-as.character(df$short)

cf<-sqldf("select CF_program, count(1) as w from tools1 group by CF_program order by w")
cf<-data.table(cf)
df<-data.table(df) #convertion names from HIH_CommonFund1.R
names(df)[1]<-"CF_program"
cf1<-df[cf,on="CF_program"]
cf1[2,2]<-cf1[2,1]
cf1[1,2]<-"BCB"
cf1[6,2]<-"BD2K"

g <- ggplot(cf1, aes(x=reorder(cf1$short,w) , cf1$w))
g + geom_bar(stat="identity", width = 0.5, fill="tomato2") + 
  labs(title="Tools per CF program", 
       subtitle="2009 - 2019", 
       y="Tools",
       x="CF Program") +
  theme(axis.text.x = element_text(angle=90, vjust=0.6,hjust = 0.95))

# --------------------- top 10 jurnals publication breakdown per groups -------------------------------------------------------------------------------------------------------------------------

journals<-unique(tools1$Journal_ISO_Abbreviation)
jg<-sqldf("select CF_program, Journal_ISO_Abbreviation, count(1) as w from tools1 group by CF_program, Journal_ISO_Abbreviation")
names(jg)<-c("CF_program","Journal","value")
jg<-jg[jg$value>1,]
jg<-df[jg,on="CF_program"]
cf1[2,2]<-cf1[2,1]
cf1[1,2]<-"BCB"
jg[jg$CF_program=="Big Data to Knowledge",'short']<-"BD2K"



# Stacked
ggplot(jg, aes(fill=Journal, y=value, x=reorder(short, value,sum ))) + 
  geom_bar(position="stack", stat="identity") +
  labs(title="Frequent publications (>2) in the same journal", 
       x = "CF Program",
       y = "Publications",
       subtitle="2009 - 2019") + 
  theme(axis.text.x = element_text(angle=90, vjust=0.6,hjust=0.95))


# --------------------- Pie chart of tools per Institution -------------------------------------------------------------------------------------------------------------------------

inst<-sqldf("select Institution, count(1) as tools from tools1 group by Institution order by tools DESC LIMIT 10")
inst<-inst[!is.na(inst$tools),]
inst$tools<-factor(inst$tools)
colnames(inst) <- c("Institution", "freq")


inst$Institution<-factor(inst$Institution,levels = inst$Institution)

pie <- ggplot(inst, aes(x =freq, y=freq, fill = Institution)) + 
  geom_bar(width = 1, stat = "identity") +
  theme(axis.line = element_blank(), 
        plot.title = element_text(hjust=0)) +
  labs(fill="Institution", 
       subtitle="2009 - 2019", 
       x=NULL, 
       y=NULL, 
       title="Top 10 tool developing institutions")
pie + coord_polar(theta = "x", start=0)

# --------------------- PCA -------------------------------------------------------------------------------------------------------------------------
ty<-sqldf("select Date_Completed_Year, count(1) as tools from tools where Date_Completed_Year< 2020 group by Date_Completed_Year")
ty$Date_Completed_Year<-as.character(ty$Date_Completed_Year)
ty[,"cum_sum"] <- cumsum(ty$tools)
ty$Date_Completed_Year<-as.numeric(ty$Date_Completed_Year)

p = ggplot() + 
  geom_line(data = ty[,1:2], aes(x = Date_Completed_Year, y = tools), color = "blue") +
  geom_line(data = ty[,c(1,3)], aes(x = Date_Completed_Year, y = cum_sum), color = "red")  +
  scale_x_continuous(name = " ", breaks = c(2009, 2010, 2011,2012,2013,2014,2015,2016,2017,2018,2019) ) +
  labs(fill="Institution", 
       subtitle="2009 - 2019", 
       x="Year", 
       y="Tools", 
       title="Tools and clumulative sum per year")

print(p)







