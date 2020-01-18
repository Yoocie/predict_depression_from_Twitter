library(kernlab)

setwd("//")

train=read.csv("trainデータの一覧.csv")

test=read.csv("testデータの一覧.csv")

svm<-ksvm(group ~., data=train)

predict<-predict(svm, test)

predict

table(predict,test$group)
