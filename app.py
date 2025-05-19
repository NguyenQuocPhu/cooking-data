from flask import Flask, render_template, request, redirect, url_for
import requests
import json
from datetime import datetime
import os
import unicodedata

app = Flask(__name__)

# Spoonacular API Key
API_KEY = 'a136ea1488074646a8e1b0eba8ba8419' 

# Hàm bỏ dấu thanh để lọc tên tiếng Việt
def remove_accents(text):
    """Chuyển đổi chữ có dấu thành không dấu."""
    nfkd_form = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

# Ánh xạ nguyên liệu Anh-Việt (140 nguyên liệu)
ingredient_translations = {
    'pork': {'vietnamese': 'Thịt lợn', 'image': 'https://tse4.mm.bing.net/th/id/OIP.qKZXtolkQyOv4KYJ0nmBQQHaFj?rs=1&pid=ImgDetMain'},
    'chicken': {'vietnamese': 'Thịt gà', 'image': 'https://tse4.mm.bing.net/th/id/OIP.tfFUV9LYoKfjDpHVJ1kP3AHaEo?rs=1&pid=ImgDetMain'},
    'tomato': {'vietnamese': 'Cà chua', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/tomato.jpg'},
    'garlic': {'vietnamese': 'Tỏi', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/garlic.jpg'},
    'fish_sauce': {'vietnamese': 'Nước mắm', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/fish-sauce.jpg'},
    'green_sticky_rice': {'vietnamese': 'Cốm', 'image': 'https://www.cet.edu.vn/wp-content/uploads/2019/04/com-xanh.jpg'},
    'beef': {'vietnamese': 'Thịt bò', 'image': 'https://tse3.mm.bing.net/th/id/OIP.177XniF-V2KMmh6B9jayJgHaE8?rs=1&pid=ImgDetMain'},
    'shrimp': {'vietnamese': 'Tôm', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/shrimp.jpg'},
    'onion': {'vietnamese': 'Hành tây', 'image': 'https://suckhoedoisong.qltns.mediacdn.vn/324455921873985536/2021/12/27/chua-yeu-sinh-ly-bang-hanh-tay-1640623099790731187596.jpg'},
    'carrot': {'vietnamese': 'Cà rốt', 'image': 'https://bhfood.vn/wp-content/uploads/2023/06/ca-rot-826.jpg'},
    'potato': {'vietnamese': 'Khoai tây', 'image': 'https://cdn.tgdd.vn/2020/10/CookProduct/10-1200x676.jpg'},
    'egg': {'vietnamese': 'Trứng', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/egg.jpg'},
    'rice': {'vietnamese': 'Gạo', 'image': 'https://nieuvang.com/wp-content/uploads/2018/05/Nhung-cong-dung-thu-vi-cua-gao-khong-phai-ai-cung-biet-%E2%80%93-Phan-2-1-e1529055633573.jpg'},
    'ginger': {'vietnamese': 'Gừng', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/ginger.jpg'},
    'lemongrass': {'vietnamese': 'Sả', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/lemongrass.jpg'},
    'chili': {'vietnamese': 'Ớt', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/chili.jpg'},
    'cucumber': {'vietnamese': 'Dưa chuột', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/cucumber.jpg'},
    'mushroom': {'vietnamese': 'Nấm', 'image': 'https://tse3.mm.bing.net/th/id/OIP.8bctv2mUAdFK27NDnNkxWwHaEK?rs=1&pid=ImgDetMain'},
    'tofu': {'vietnamese': 'Đậu phụ', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/tofu.jpg'},
    'cabbage': {'vietnamese': 'Bắp cải', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/cabbage.jpg'},
    'spinach': {'vietnamese': 'Rau cải', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/spinach.jpg'},
    'bell_pepper': {'vietnamese': 'Ớt chuông', 'image': 'https://th.bing.com/th/id/R.c29588248f8a859ee76bcab457009a5a?rik=%2bLyd%2fd4F9AaNlw&pid=ImgRaw&r=0'},
    'eggplant': {'vietnamese': 'Cà tím', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/eggplant.jpg'},
    'soy_sauce': {'vietnamese': 'Nước tương', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/soy-sauce.jpg'},
    'lime': {'vietnamese': 'Chanh', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/lime.jpg'},
    'coconut_milk': {'vietnamese': 'Nước cốt dừa', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/coconut-milk.jpg'},
    'basil': {'vietnamese': 'Húng quế', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/basil.jpg'},
    'mint': {'vietnamese': 'Húng bạc hà', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/mint.jpg'},
    'cilantro': {'vietnamese': 'Rau mùi', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/cilantro.jpg'},
    'green_onion': {'vietnamese': 'Hành lá', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/green-onion.jpg'},
    'sweet_potato': {'vietnamese': 'Khoai lang', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/sweet-potato.jpg'},
    'broccoli': {'vietnamese': 'Bông cải xanh', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/broccoli.jpg'},
    'cauliflower': {'vietnamese': 'Súp lơ', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/cauliflower.jpg'},
    'zucchini': {'vietnamese': 'Bí ngòi', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/zucchini.jpg'},
    'corn': {'vietnamese': 'Ngô', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/corn.jpg'},
    'green_bean': {'vietnamese': 'Đậu cô-ve', 'image': 'https://tse1.mm.bing.net/th/id/OIP.Y2Kmbno-ZrmKWCNR_CbsFwHaC2?rs=1&pid=ImgDetMain'},
    'peanut': {'vietnamese': 'Đậu phộng', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/peanuts.jpg'},
    'sesame_oil': {'vietnamese': 'Dầu mè', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/sesame-oil.jpg'},
    'oyster_sauce': {'vietnamese': 'Dầu hào', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/oyster-sauce.jpg'},
    'rice_noodle': {'vietnamese': 'Bún', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/rice-noodles.jpg'},
    'morning_glory': {'vietnamese': 'Rau muống', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/water-spinach.jpg'},
    'bitter_melon': {'vietnamese': 'Khổ qua', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/bitter-melon.jpg'},
    'daikon': {'vietnamese': 'Củ cải trắng', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/daikon.jpg'},
    'bamboo_shoot': {'vietnamese': 'Măng', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/bamboo-shoots.jpg'},
    'lotus_root': {'vietnamese': 'Củ sen', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/lotus-root.jpg'},
    'taro': {'vietnamese': 'Khoai môn', 'image': 'https://doiduavang.vn/wp-content/uploads/2021/01/cu-khoai-mon-le-pho-e1611128325344.jpg'},
    'fish': {'vietnamese': 'Cá', 'image': 'https://tse3.mm.bing.net/th/id/OIP.x--NmrvLamCQnocaw8I6TwHaEK?rs=1&pid=ImgDetMain'},
    'squid': {'vietnamese': 'Mực', 'image': 'https://th.bing.com/th/id/R.0fc4dffdb31a824fc33caac8c4069cb8?rik=skTbA2TYZclaYA&pid=ImgRaw&r=0'},
    'clam': {'vietnamese': 'Nghêu', 'image': 'https://tse3.mm.bing.net/th/id/OIP.xBaNvZTuvjxGl36IkdDFMwHaE8?rs=1&pid=ImgDetMain'},
    'crab': {'vietnamese': 'Cua', 'image': 'https://tse1.mm.bing.net/th/id/OIP.P1VHAo9uzl4vsNI3BWQZBAHaEK?rs=1&pid=ImgDetMain'},
    'turmeric': {'vietnamese': 'Nghệ', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/turmeric.jpg'},
    'galangal': {'vietnamese': 'Riềng', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/galangal.jpg'},
    'shallot': {'vietnamese': 'Hành tím', 'image': 'https://toplist.vn/images/800px/chong-loang-xuong-484868.jpg'},
    'black_pepper': {'vietnamese': 'Tiêu đen', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/black-pepper.jpg'},
    'chili_powder': {'vietnamese': 'Ớt bột', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/chili-powder.jpg'},
    'star_anise': {'vietnamese': 'Hồi', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/star-anise.jpg'},
    'cinnamon': {'vietnamese': 'Quế', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/cinnamon.jpg'},
    'mung_bean': {'vietnamese': 'Đậu xanh', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/mung-beans.jpg'},
    'sticky_rice': {'vietnamese': 'Gạo nếp', 'image': 'https://caogam.vn/sites/default/files/styles/anh_og_image/public/2021-03/anh-gao-nep.jpg?itok=rmJdgbo6'},
    'vermicelli': {'vietnamese': 'Miến', 'image': 'https://cdn.tgdd.vn/Files/2017/06/27/997201/cach-phan-biet-va-su-dung-cac-loai-mien2_800x400.jpg'},
    'pho_noodle': {'vietnamese': 'Bánh phở', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/rice-noodles.jpg'},
    'rice_paper': {'vietnamese': 'Bánh tráng', 'image': 'https://truonghaifood.com/wp-content/uploads/2022/04/banh-trang-gao-tron-me-th-food-2.jpg'},
    'banana_leaf': {'vietnamese': 'Lá chuối', 'image': 'https://tse3.mm.bing.net/th/id/OIP.6P6_OSlpDIciIi5iRu786AHaEK?rs=1&pid=ImgDetMain'},
    'pork_belly': {'vietnamese': 'Thịt ba chỉ', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/pork-belly.jpg'},
    'duck': {'vietnamese': 'Vịt', 'image': 'https://tse1.mm.bing.net/th/id/OIP.tPDL07DbVSZH2I-rz2_tggHaE7?rs=1&pid=ImgDetMain'},
    'catfish': {'vietnamese': 'Cá tra', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/catfish.jpg'},
    'tilapia': {'vietnamese': 'Cá rô phi', 'image': 'https://tse4.mm.bing.net/th/id/OIP.jk-IOevV32MuKQPKG1H2gQHaEt?rs=1&pid=ImgDetMain'},
    'snakehead_fish': {'vietnamese': 'Cá lóc', 'image': 'https://cdn.tgdd.vn/2021/10/CookRecipe/CookTipsNote/ca-loc-la-ca-gi-ca-loc-bao-nhieu-calo-va-an-ca-loc-co-tac-tipsnote-800x450-1.jpg'},
    'okra': {'vietnamese': 'Đậu bắp', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/okra.jpg'},
    'winter_melon': {'vietnamese': 'Bí đao', 'image': 'https://vinmec-prod.s3.amazonaws.com/images/20200610_153300_830912_nuoc-ep-bi-dao.max-1800x1800.jpg'},
    'chayote': {'vietnamese': 'Su su', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/chayote.jpg'},
    'watercress': {'vietnamese': 'Cải xoong', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/watercress.jpg'},
    'amaranth': {'vietnamese': 'Rau dền', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/amaranth.jpg'},
    'mustard_greens': {'vietnamese': 'Cải xanh', 'image': 'https://tse2.mm.bing.net/th/id/OIP.gMEStYFMUyhGhM4jLGmxJQHaHS?rs=1&pid=ImgDetMain'},
    'perilla': {'vietnamese': 'Tía tô', 'image': 'https://binhdienonline.com/thumbs_size/product/2021_02/tia-to/[1200x1200-cr]tia-to--8.jpg'},
    'sawtooth_herb': {'vietnamese': 'Ngò gai', 'image': 'https://th.bing.com/th/id/R.8813ed1682b5471726d3a67a4b3a5154?rik=rzNA3ycOJ2mbOQ&pid=ImgRaw&r=0'},
    'dill': {'vietnamese': 'Thì là', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/dill.jpg'},
    'tamarind': {'vietnamese': 'Me', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/tamarind.jpg'},
    'fermented_shrimp_paste': {'vietnamese': 'Mắm tôm', 'image': 'https://tse3.mm.bing.net/th/id/OIP.Kac4pu5M5LxV11g0fyVX8wHaEK?rs=1&pid=ImgDetMain'},
    'pork_liver': {'vietnamese': 'Gan lợn', 'image': 'https://media.2dep.vn/upload/hamynguyen/2022/02/18/mua-gan-lon-nho-de-y-ky-3-dieu-nay-keo-anh-huong-den-suc-khoe-cua-ca-gia-dinh-social-1645176704.jpg'},
    'chicken_feet': {'vietnamese': 'Chân gà', 'image': 'https://th.bing.com/th/id/R.5b170ba391b4fd70c33e8f5f8d58134c?rik=7bIYsCIS9%2bO8Yg&pid=ImgRaw&r=0'},
    'pork_rind': {'vietnamese': 'Tóp mỡ', 'image': 'https://www.noichienkhongdau.com/wp-content/uploads/2021/12/lam-top-mo-bang-noi-chien-khong-dau-.jpg'},
    'blood_sausage': {'vietnamese': 'Dồi tiết', 'image': 'https://img-global.cpcdn.com/recipes/b8289dd2293e8b81/1200x630cq70/photo.jpg'},
    'lemongrass_paste': {'vietnamese': 'Sả băm', 'image': 'https://kinhnghiemnongnghiep.com/wp-content/uploads/2022/03/s%E1%BA%A3.jpg'},
    'mango': {'vietnamese': 'Xoài', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/mango.jpg'},
    'pineapple': {'vietnamese': 'Dứa', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/pineapple.jpg'},
    'banana': {'vietnamese': 'Chuối', 'image': 'https://nld.mediacdn.vn/2016/chuoitrinutgotchan-1479781920955.jpg'},
    'jackfruit': {'vietnamese': 'Mít', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/jackfruit.jpg'},
    'durian': {'vietnamese': 'Sầu riêng', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/durian.jpg'},
    'dragon_fruit': {'vietnamese': 'Thanh long', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/dragon-fruit.jpg'},
    'longan': {'vietnamese': 'Nhãn', 'image': 'https://th.bing.com/th/id/R.ab0afeb4c3a0af1658e47471fc20fce3?rik=xvzm4ZDhOLjB0A&pid=ImgRaw&r=0'},
    'lychee': {'vietnamese': 'Vải', 'image': 'https://tse2.mm.bing.net/th/id/OIP.S-mry04TS13qFmvZ8f53ewHaEq?rs=1&pid=ImgDetMain'},
    'rambutan': {'vietnamese': 'Chôm chôm', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/rambutan.jpg'},
    'pomelo': {'vietnamese': 'Bưởi', 'image': 'https://tse2.mm.bing.net/th/id/OIP.tBc6j0qJLUX1hDssY1gY5AHaHa?rs=1&pid=ImgDetMain'},
    'guava': {'vietnamese': 'Ổi', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/guava.jpg'},
    'papaya': {'vietnamese': 'Đu đủ', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/papaya.jpg'},
    'watermelon': {'vietnamese': 'Dưa hấu', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/watermelon.jpg'},
    'coconut': {'vietnamese': 'Dừa', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/coconut.jpg'},
    'custard_apple': {'vietnamese': 'Mãng cầu', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/custard-apple.jpg'},
    'starfruit': {'vietnamese': 'Khế', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/starfruit.jpg'},
    'sweet_sop': {'vietnamese': 'Na', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/custard-apple.jpg'},
    'pork_rib': {'vietnamese': 'Sườn lợn', 'image': 'https://tse4.mm.bing.net/th/id/OIP.MXaDwe2mEJc-K5zFhvLiegHaFj?rs=1&pid=ImgDetMain'},
    'chicken_wing': {'vietnamese': 'Cánh gà', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/chicken-wings.jpg'},
    'chicken_breast': {'vietnamese': 'Ức gà', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/chicken-breast.jpg'},
    'beef_brisket': {'vietnamese': 'Thịt bò gầu', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/beef-brisket.jpg'},
    'beef_tendon': {'vietnamese': 'Gân bò', 'image': 'https://th.bing.com/th/id/R.1a926ac8631d2ea8d8254780e29380d0?rik=%2ffdJFbc%2bzvmv9g&pid=ImgRaw&r=0'},
    'pork_hock': {'vietnamese': 'Chân giò lợn', 'image': 'https://tse3.mm.bing.net/th/id/OIP.Mwtdvpsup2Dk-63erv5NOQHaGT?rs=1&pid=ImgDetMain'},
    'mackerel': {'vietnamese': 'Cá thu', 'image': 'https://tse3.mm.bing.net/th/id/OIP.Z1quRox7QSCp7x_9imoRsgHaHa?rs=1&pid=ImgDetMain'},
    'anchovy': {'vietnamese': 'Cá cơm', 'image': 'https://th.bing.com/th/id/R.612ce47dfc58e2257034e29cb1ebbb33?rik=WdZSeTnnNS8KdQ&pid=ImgRaw&r=0'},
    'prawn': {'vietnamese': 'Tôm sú', 'image': 'https://th.bing.com/th/id/R.fdfa7b351ef7b38a28f84bb80e30788a?rik=i8Ea8V0Te4F1pg&pid=ImgRaw&r=0'},
    'scallop': {'vietnamese': 'Sò điệp', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/scallops.jpg'},
    'oyster': {'vietnamese': 'Hàu', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/oysters.jpg'},
    'fermented_fish_sauce': {'vietnamese': 'Mắm cá', 'image': 'https://dacsanchinhgoc.vn/upload/images/mam-ca-com-1.jpg'},
    'fermented_bean_paste': {'vietnamese': 'Tương', 'image': 'https://tse1.mm.bing.net/th/id/OIP.qwchoDMy_TOgCpMfMcGlygHaEL?rs=1&pid=ImgDetMain'},
    'sesame_seed': {'vietnamese': 'Vừng', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/sesame-seeds.jpg'},
    'annatto_seed': {'vietnamese': 'Hạt điều màu', 'image': 'https://3.bp.blogspot.com/-FzdpeAipZaw/XCbnJJq9ohI/AAAAAAAAESI/R8UKLsgIl5Aa5NJ4NTbkO5G2A8CP3QibACLcBGAs/w1200-h630-p-k-no-nu/h%25E1%25BA%25A1t%2B%25C4%2591i%25E1%25BB%2581u%2Bm%25C3%25A0u%252C%2Bh%25E1%25BA%25A1t%2Bc%25C3%25A0%2Bri%252C%2Bh%25E1%25BA%25A1t%2B%25C4%2591i%25E1%25BB%2581u%2Bnhu%25E1%25BB%2599m.jpg'},
    'dried_shrimp': {'vietnamese': 'Tôm khô', 'image': 'https://amthuc10phut.vn/wp-content/uploads/2023/04/1-54.png'},
    'dried_squid': {'vietnamese': 'Mực khô', 'image': 'https://tse2.mm.bing.net/th/id/OIP.PQXtvW0cvLYbE2iyJvE4igHaHa?rs=1&pid=ImgDetMain'},
    'lotus_seed': {'vietnamese': 'Hạt sen', 'image': 'https://cdn.nhathuoclongchau.com.vn/unsafe/800x0/filters:quality(95)/https://cms-prod.s3-sgn09.fptcloud.com/sen_4_ab94004c0b.jpg'},
    'black_bean': {'vietnamese': 'Đậu đen', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/black-beans.jpg'},
    'red_bean': {'vietnamese': 'Đậu đỏ', 'image': 'https://tse1.mm.bing.net/th/id/OIP.GpvhwAI0Hs1Td9Yu6BHfTwHaE8?rs=1&pid=ImgDetMain'},
    'water_chestnut': {'vietnamese': 'Củ năng', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/water-chestnuts.jpg'},
    'jicama': {'vietnamese': 'Củ đậu', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/jicama.jpg'},
    'chinese_cabbage': {'vietnamese': 'Cải thảo', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/napa-cabbage.jpg'},
    'bok_choy': {'vietnamese': 'Cải thìa', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/bok-choy.jpg'},
    'malabar_spinach': {'vietnamese': 'Rau mồng tơi', 'image': 'https://tse3.mm.bing.net/th/id/OIP.FD25i-wJTs_9zMzjVW6gRwHaGn?rs=1&pid=ImgDetMain'},
    'pennywort': {'vietnamese': 'Rau má', 'image': 'https://bepmina.vn/wp-content/uploads/2023/04/rau-ma.jpeg'},
    'banana_blossom': {'vietnamese': 'Bắp chuối', 'image': 'https://tse1.mm.bing.net/th/id/OIP.7N-tpKbh69y_CfSzADtLmwHaEK?rs=1&pid=ImgDetMain'},
    'betel_leaf': {'vietnamese': 'Lá lốt', 'image': 'https://bvnguyentriphuong.com.vn/uploads/082021/images/la-lot-chua-dau-nhuc.jpg'},
    'fish_mint': {'vietnamese': 'Rau diếp cá', 'image': 'https://tse1.mm.bing.net/th/id/OIP.pJ58eIjfWZNhi5zRFOeOzQHaHa?rs=1&pid=ImgDetMain'},
    'vietnamese_coriander': {'vietnamese': 'Rau răm', 'image': 'https://cdn.shopify.com/s/files/1/0367/6189/4956/products/sesofoods-rau-ram_1_1200x1200.jpg?v=1601124372'},
    'spring_roll_wrapper': {'vietnamese': 'Bánh tráng rế', 'image': 'https://cdn.tgdd.vn/Files/2021/09/15/1382886/cach-tu-lam-banh-trang-re-cuon-cha-gio-chien-don-gian-nhanh-chong-202109151348560562.jpg'},
    'glutinous_rice_flour': {'vietnamese': 'Bột nếp', 'image': 'https://tse3.mm.bing.net/th/id/OIP.uvKOTymgAelFUpiA024zTwHaE9?rs=1&pid=ImgDetMain'},
    'tapioca_starch': {'vietnamese': 'Bột năng', 'image': 'https://daotaobeptruong.vn/images/daotaobeptruong/bot_nang_la_thuc_pham_pho_bien.png'},
    'rice_flour': {'vietnamese': 'Bột gạo', 'image': 'https://tse1.mm.bing.net/th/id/OIP.kkmojsT9_RcdM0R22m2ptgAAAA?rs=1&pid=ImgDetMain'},
    'pork_paste': {'vietnamese': 'Chả lụa', 'image': 'https://www.disneycooking.com/wp-content/uploads/2021/01/cha-lua.jpg'},
    'fermented_pork': {'vietnamese': 'Nem chua', 'image': 'https://media-cdn-v2.laodong.vn/Storage/NewsPortal/2022/10/22/1108043/Fanpage-NEM-CHUA-THA.jpg'},
    'dried_mushroom': {'vietnamese': 'Nấm khô', 'image': 'https://tse1.mm.bing.net/th/id/OIP.YsipsUb1tlv2bFgCEFwTSAHaHa?w=1200&h=1200&rs=1&pid=ImgDetMain'},
    'wood_ear_mushroom': {'vietnamese': 'Nấm mèo', 'image': 'https://tse3.mm.bing.net/th/id/OIP.mSl6ftcqXr3s-4jQyQu94AHaHa?rs=1&pid=ImgDetMain'},
    'lemongrass_tea': {'vietnamese': 'Trà sả', 'image': 'https://tse2.mm.bing.net/th/id/OIP.xHYHyApAHYO4Oqf3B7uOWgHaFj?rs=1&pid=ImgDetMain'},
    'pork_blood': {'vietnamese': 'Tiết lợn', 'image': 'https://tse4.mm.bing.net/th/id/OIP.idl3WhAiMq6ZASdSgSobBAHaE8?rs=1&pid=ImgDetMain'},
    'chicken_liver': {'vietnamese': 'Gan gà', 'image': 'https://spoonacular.com/cdn/ingredients_100x100/chicken-liver.jpg'},
}

# File để lưu lịch sử
HISTORY_FILE = 'history.json'

# Đọc lịch sử từ file JSON
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            return []
    print("File does not exist")
    return []

# Lưu lịch sử vào file JSON
def save_history(entry):
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, default=str)

@app.route('/', methods=['GET', 'POST'])
def index():
    recipes = []
    ingredients = request.form.get('ingredients', '') if request.method == 'POST' else request.args.get('ingredients', '')
    
    if request.method == 'POST':
        url = 'https://api.spoonacular.com/recipes/findByIngredients'
        params = {
            'ingredients': ingredients.replace(' ', ''),
            'number': 100,
            'apiKey': API_KEY
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            recipes = response.json()
            # Ánh xạ tên nguyên liệu sang tiếng Việt
            for recipe in recipes:
                for ing in recipe.get('usedIngredients', []):
                    ing['vietnamese'] = ingredient_translations.get(ing.get('name', ''), {}).get('vietnamese', ing.get('name', ''))
                for ing in recipe.get('missedIngredients', []):
                    ing['vietnamese'] = ingredient_translations.get(ing.get('name', ''), {}).get('vietnamese', ing.get('name', ''))
        return render_template('index.html', recipes=recipes, ingredients=ingredients)
    
    return render_template('index.html', recipes=recipes, ingredients=ingredients)

@app.route('/recipe/<int:id>')
def recipe(id):
    url = f'https://api.spoonacular.com/recipes/{id}/information'
    params = {'apiKey': API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        recipe = response.json()
        for ing in recipe.get('extendedIngredients', []):
            ing['vietnamese'] = ingredient_translations.get(ing.get('name', ''), {}).get('vietnamese', ing.get('name', ''))
        return render_template('recipe.html', recipe=recipe)
    return 'Error fetching recipe', 500

@app.route('/save_recipe/<int:id>', methods=['POST'])
def save_recipe(id):
    url = f'https://api.spoonacular.com/recipes/{id}/information'
    params = {'apiKey': API_KEY}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        recipe = response.json()
        save_history({
            'title': recipe['title'],
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ingredients_searched': request.form.get('ingredients', ''),
            'ingredients_recipe': [ing['original'] for ing in recipe.get('extendedIngredients', [])]
        })
        for ing in recipe.get('extendedIngredients', []):
            ing['vietnamese'] = ingredient_translations.get(ing.get('name', ''), {}).get('vietnamese', ing.get('name', ''))
        return render_template('recipe.html', recipe=recipe, message="Đã lưu món ăn vào lịch sử!")
    return 'Error saving recipe', 500

@app.route('/ingredients')
def ingredients():
    selected_letter = request.args.get('letter', '').upper()
    sorted_ingredients = sorted(
        [{'english': key, 'vietnamese': value['vietnamese'], 'image': value['image']} 
         for key, value in ingredient_translations.items()],
        key=lambda x: remove_accents(x['vietnamese'])
    )
    if selected_letter:
        sorted_ingredients = [
            ing for ing in sorted_ingredients 
            if remove_accents(ing['vietnamese'])[0].upper() == selected_letter
        ]
    return render_template('ingredients.html', ingredients=sorted_ingredients, selected_letter=selected_letter)

@app.route('/history')
def history():
    history = load_history()
    return render_template('history.html', history=history)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
