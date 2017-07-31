$(function() {
	//导航条切换
	$(".top ul li").each(function(index) {
		$(this).click(function() {
			$("li").removeClass("active");
			$("li").eq(index).addClass("active");
		});
	});
	
/*********************悬浮切换图片*************************/
	
	$("#xia").mouseover(function(){
		$(this).find("img").attr("src","static/img/iphone-1.png");
	}).mouseout(function(){
		$(this).find("img").attr("src","static/img/iphone.png");
	})
	$("#zai").mouseover(function(){
		$(this).find("img").attr("src","static/img/android-1.png");
	}).mouseout(function(){
		$(this).find("img").attr("src","static/img/android.png");
	})
})