# column names convertions 
# https://docs.google.com/spreadsheets/d/1ndVY8Q2LOaZO_P_HDmSQulagjeUrS250mAL2N5V8GvY/edit#gid=0
tool_names<-data.frame(names(tools_new))
tool_names$old_name<-''
names(tool_names)[1]<-'new_name'
tool_names[2,2]<-"tool_URL"
tool_names[3,2]<-"tool_name"
tool_names[4,2]<-"tool_description"
tool_names[5,2]<-"PMID"
tool_names[6,2]<-"PMC"
tool_names[7,2]<-"doi"
tool_names[8,2]<-"Article.ArticleTitle"
tool_names[9,2]<-"Article.Abstract.AbstractText"
tool_names[10,2]<-"Article.AuthorList"
tool_names[11,2]<-"Article.ELocationID"
tool_names[12,2]<-"Article.PublicationTypeList"
tool_names[13,2]<-"Article.Abstract.CopyrightInformation"
tool_names[14,2]<-"Article.GrantList"
tool_names[15,2]<-"ChemicalList"
tool_names[16,2]<-"pmc_ids"
tool_names[17,2]<-"num_citations"
tool_names[18,2]<-"Article.Language"
tool_names[19,2]<-"KeywordList"
tool_names[20,2]<-"last_updated"
tool_names[21,2]<-"added_on"
tool_names[22,2]<-"DateRevised.Month"
tool_names[23,2]<-"DateRevised.Day"
tool_names[24,2]<-"DateRevised.Year"
tool_names[25,2]<-"DateCompleted.Day"
tool_names[26,2]<-"DateCompleted.Month"
tool_names[27,2]<-"DateCompleted.Yesr"
tool_names[28,2]<-"published_on"
tool_names[29,2]<-"Article.ArticleDate"
tool_names[30,2]<-"journal"
tool_names[31,2]<-"Article.Journal.ISSN"
tool_names[32,2]<-"Article.Journal.Title"
tool_names[33,2]<-"Article.Journal.ISOAbbreviation"
tool_names[34,2]<-"subjects"
tool_names[35,2]<-"publisher_subjects"
tool_names[36,2]<-"Article.Journal.JournalIssue.Issue"
tool_names[37,2]<-"Article.Journal.JournalIssue.Volume"
tool_names[38,2]<-"Article.Journal.JournalIssue.PubDate.Day"
tool_names[39,2]<-"Article.Journal.JournalIssue.PubDate.Month"
tool_names[40,2]<-"Article.Journal.JournalIssue.PubDate.Year"
tool_names[41,2]<-"MedlineJournalInfo.MedlineTA"
tool_names[42,2]<-"MedlineJournalInfo.NlmUniqueID"
tool_names[43,2]<-"MedlineJournalInfo.Country"
tool_names[44,2]<-"MedlineJournalInfo.ISSNLinking"
tool_names[45,2]<-"Article.Journal.JournalIssue.PubDate.Month"
tool_names[45,2]<-"Article.Pagination.MedlinePgn"
tool_names[46,2]<-"MeshHeadingList"
tool_names[47,2]<-"altmetric_id"
tool_names[48,2]<-"score"
tool_names[49,2]<-"altmetric_jid"
tool_names[50,2]<-"context.journal.count"
tool_names[51,2]<-"context.similar_age_journal_3m.pct"
tool_names[52,2]<-"context_similar_age_3m_count"
tool_names[53,2]<-"context.all.rank"
tool_names[54,2]<-"readers_count"
tool_names[55,2]<-"readers.mendeley"
tool_names[56,2]<-"readers.connotea"
tool_names[57,2]<-"readers.citeulike"
tool_names[58,2]<-"cited_by_posts_count"
tool_names[59,2]<-"cited_by_tweeters_count"
tool_names[60,2]<-"cohorts.pub"
tool_names[61,2]<-"context.journal.higher_than"
tool_names[62,2]<-"context_journal_pct"
tool_names[63,2]<-"context_similar_age_3m_pct"
tool_names[64,2]<-"context.similar_age_3m.rank"
tool_names[65,2]<-"context.journal.rank"
tool_names[66,2]<-"context.similar_age_journal_3m.rank"
tool_names[67,2]<-"context.all.mean"
tool_names[68,2]<-"context.similar_age_3m.mean"
tool_names[69,2]<-"context.journal.mean"
tool_names[70,2]<-"context.similar_age_journal_3m.mean"
tool_names[71,2]<-"context.similar_age_3m.count"
tool_names[72,2]<-"context.similar_age_journal_3m.higher_than"
tool_names[73,2]<-"cohorts.sci"
tool_names[74,2]<-"cited_by_msm_count"
tool_names[75,2]<-"cited_by_accounts_count"
tool_names[76,2]<-"cited_by_fbwalls_count"
tool_names[77,2]<-"context.similar_age_3m.higher_than"
tool_names[78,2]<-"details_url"

tool_names$source<-''
tool_names[1:32,3]<-"PubMed"
tool_names[33:77,3]<-"Altmetric"












