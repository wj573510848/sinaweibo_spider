# encoding=utf-8



from items import InterestingArea



class MyTextPipeline(object):
    def __init__(self):
        self.count=1
    
    def process_item(self,item,spider):
        if isinstance(item, InterestingArea):
            a=item['content']
            b=item['review_url']
            c=item['review']
            a=" ".join(a)
            f=open("weibodata.txt",'ab')
            print("***********at beginning of saving**********")
            f.write('\r\n')
            f.write("%s.***URL:" % self.count)
            f.write(b)
            if a:
                f.write("\r\n")
                f.write("Content:")
                f.write("\r\n")
                f.write(a)
            if c:
                f.write("\r\n")
                f.write("Review:")
                for text in c:
                    f.write("\r\n")
                    f.write(text)
            f.close()
            print("saved! This is  %s items." % self.count)
            self.count = self.count +1
        return item
        
