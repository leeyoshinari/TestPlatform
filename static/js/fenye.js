/**
 * 对页面进行分页
 * @param obj 页码标签对象
 * @param  pageNum 分页总数
 * @param  pageSize number 分页大小
 * @param currentPage number 当前页
 */

function PagingManage(obj, pageNum, currentPage) {
    if (obj) {
        let currentpage = currentPage;//当前页面
        let showPageNum = 6;//显示多少个页码

        let pagehtml = "";
        let divId = "" + obj.attr('id');

        //只有一页内容
        if (pageNum <= 1) {
            pagehtml = "";
        }

        //大于一页内容
        if (pageNum > 1) {
            if (currentpage > 1) {
                pagehtml += '<li><a href="javascript:void(0);" onclick="switchPage(\'' + divId + '\',' + (currentpage - 1) + ')">上一页</a></li>';
            }

            let startPage = 1;
            //计算页码开始位置
            if (showPageNum > pageNum) {//如果要显示的页码大于总的页码数
                startPage = 1
            } else {//如果要显示的页码小于总的页码数
                if (currentpage - (showPageNum / 2) <= 0) {//如果当前页面
                    startPage = 1;
                } else if (currentpage + (showPageNum / 2) >= pageNum) {
                    startPage = pageNum - showPageNum;
                } else {
                    startPage = currentpage - (showPageNum / 2);
                }
            }

            startPage = parseInt(startPage);
            if (currentPage === 1){
                pagehtml += '<li><a href="javascript:void(0);" onclick="switchPage(\'' + divId + '\',' + 1 + ')">上一页</a></li>';
            } else {
                pagehtml += '<li><a href="javascript:void(0);" onclick="switchPage(\'' + divId + '\',' + (currentpage - 1) + ')">上一页</a></li>';
            }

            for (let i = startPage; i < (startPage + showPageNum); i++) {
                //如果要输出的页面大于总的页面数,则退出
                if (i > pageNum) {
                    break;
                }
                if (i === currentpage) {
                    pagehtml += '<li><a class="active" href="javascript:void(0);" onclick="switchPage(\'' + divId + '\', ' + i + ')">' + i + '</a></li>';
                } else {
                    pagehtml += '<li><a href="javascript:void(0);" onclick="switchPage(\'' + divId + '\', ' + i + ')">' + i + '</a></li>';
                }
            }
            if (currentpage < pageNum) {
                pagehtml += '<li><a href="javascript:void(0);" onclick="switchPage(\'' + divId + '\',' + (currentpage + 1) + ')">下一页</a></li>';
            }
        }
        obj.html(pagehtml);
    }
}

