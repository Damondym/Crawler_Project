import requests
import json

def search_download_csr(year):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
               #":authority":"goldenbee.applysquare.com",
               #":path":"/ajax/graphql",]
               "cookie":"_a2_csrf=MTU0MjM4NDY3MnxJalZGUjBacWNtVnNiVFJyWjJSSVdYcHViRlozWWxWVVZFaE5hRTFMZW1kbVVtMUtibEJzUm5jelVsVTlJZ289fCRL3Xu0daSzhC8eq7Js7iLTd2FmE2lEISbt0-cWUb2w; csrftoken=rUkUrrFwRb%2FYcAyGihEasQDbFskfyN1nrjrCBWn4ubJJCJEgBtXeNvgEerUURGrcRAgKAVPj5XjoWKU7OIhkpw%3D%3D",
               "origin":"https://goldenbee.applysquare.com",
               "referer":"https://goldenbee.applysquare.com/retrieval/list",
               "x-csrftoken":"rUkUrrFwRb/YcAyGihEasQDbFskfyN1nrjrCBWn4ubJJCJEgBtXeNvgEerUURGrcRAgKAVPj5XjoWKU7OIhkpw==",
               "x-requested-with":"XMLHttpRequest"
               }

    payload={"query":"""
    query($q: String, $year: Int
        $company: InputGoldenbeeReportSearchParamCompany,
        $offset: Int!, $limit: Int!
        $review:  InputGoldenbeeReportSearchParamReview){
        goldenbee{
            report{
                search(q:$q, company: $company,review: $review,
                    year: $year,
                    offset: $offset, limit: $limit){
                    items{
                        doc_name
                        company{
                            name
                            industry
                            nature
                            scale
                            sub_industry
                            num_of_published_report
                        }
                        company_id
                        id
                        doc(q:$q){
                            matched_doc_paragraph
                            cover_url
                            images{
                                url
                            }
                        }
                        status
                        year
                        review{
                            body{
                                parameters{
                                    name{
                                        key
                                        value
                                    }
                                    pages_num
                                }
                            }
                            commited_time
                        }
                    }
                    page_info{
                        count
                        offset
                    }
                }
            }
        }
    }""",
             "variables":"{\"company\": {}, \"review\": {\"lang\":\"cn\"}, \"offset\": 0, \"limit\": 5000,\"year\":"+str(year+1)+"}"
    }
    url="https://goldenbee.applysquare.com/ajax/graphql"
    r=requests.post(url,headers=headers,params=payload)
    print(r)
    js=json.loads(r.text)
    items = js["data"]["goldenbee"]["report"]["search"]["items"]
    b=0
    for i in items:
        b += 1
        company = i["company"]
        if company != None:
            doc_name = i["doc_name"]
            crs_id = i["id"]
            nature = company["nature"]
            if len(nature) != 0 and doc_name != "empty_doc_alias_placeholder" and doc_name != None:
                if_waizi = False
                for n in nature:
                    if n == "waizi":
                        if_waizi = True
                if not if_waizi:
                    print(doc_name+str(b))
                    url2 = "https://goldenbee.applysquare.com/doc/download?doc-reports="+crs_id
                    r2 = requests.get(url2)
                    with open("F:/python项目/金蜜蜂CSR/"+str(year)+"/"+doc_name+".zip", "wb") as code:
                         code.write(r2.content)

#search_download_csr(2016)
#search_download_csr(2015)
search_download_csr(2014)
search_download_csr(2013)
