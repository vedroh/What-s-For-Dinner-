import requests
from recipe_scrapers import scrape_html
import pandas as pd


urls = [
    #bonappetit
    "https://www.bonappetit.com/recipe/gnocchi-piccata",
    "https://www.bonappetit.com/recipe/creamy-fondue-beans",
    "https://www.bonappetit.com/recipe/smothered-italian-sausage",
    "https://www.bonappetit.com/recipe/asian-pear-salad-with-crispy-shallots",
    "https://www.bonappetit.com/recipe/feta-and-sun-dried-tomato-dip",
    "https://www.bonappetit.com/recipe/smoky-brown-butter-pasta",
    "https://www.bonappetit.com/recipe/shrimp-salad",
    "https://www.bonappetit.com/recipe/sweet-and-spicy-zucchini",
    "https://www.bonappetit.com/recipe/zaru-soba",
    "https://www.bonappetit.com/recipe/boozy-cherry-chocolate-pavlova",
    "https://www.bonappetit.com/recipe/homemade-hobnob-biscuits-crunchy-oat-cookies",
    "https://www.bonappetit.com/recipe/chicken-breakfast-sausages",
    "https://www.bonappetit.com/recipe/tomato-aguachile",
    "https://www.bonappetit.com/recipe/corn-furikake-fried-rice",
    "https://www.bonappetit.com/recipe/chocolate-mug-cake",
    "https://www.bonappetit.com/recipe/speedy-chicken-stroganoff",
    "https://www.bonappetit.com/recipe/harissa-scampi",
    "https://www.bonappetit.com/recipe/quick-chicken-cordon-bleu",
    "https://www.bonappetit.com/recipe/steakhouse-salad-with-black-pepper-dressing",
    "https://www.bonappetit.com/recipe/best-chicken-and-dumplings",
    "https://www.bonappetit.com/recipe/weeknight-pumpkin-chili",
    "https://www.bonappetit.com/recipe/one-pot-chicken-thighs-with-cilantro-rice-and-beans",
    "https://www.bonappetit.com/recipe/cod-with-lemon-butter-sauce",
    "https://www.bonappetit.com/recipe/roasted-cauliflower-salad-with-feta-and-dates",
    "https://www.bonappetit.com/recipe/sheet-pan-pomegranate-chicken-with-walnut-relish",
    "https://www.bonappetit.com/recipe/sheet-pan-pierogies-and-beets",
    "https://www.bonappetit.com/recipe/sheet-pan-salmon-with-rice-cakes-and-kimchi",
    "https://www.bonappetit.com/recipe/miso-mayo-chicken-bowl",
    "https://www.bonappetit.com/recipe/baked-sweet-potato-chaat",
    "https://www.bonappetit.com/recipe/turkey-stuffing-meatballs",
    "https://www.bonappetit.com/recipe/herby-salmon-potato-salad",
    "https://www.bonappetit.com/recipe/green-pasta-e-fagioli",
    "https://www.bonappetit.com/recipe/chicken-cabbage-stir-fry",
    "https://www.bonappetit.com/recipe/sausage-with-charred-cabbage-and-giardiniera",
    "https://www.bonappetit.com/recipe/buttermilk-corn-pasta",
    "https://www.bonappetit.com/recipe/pad-kra-pao",
    "https://www.bonappetit.com/recipe/best-ever-grilled-cheese",
    "https://www.bonappetit.com/recipe/spicy-carrot-rigatoni",
    "https://www.bonappetit.com/recipe/classic-tuna-melt",
    "https://www.bonappetit.com/recipe/mushroom-farrotto",
    "https://www.bonappetit.com/recipe/caramelized-cabbage",
    "https://www.bonappetit.com/recipe/homemade-bagels",
    "https://www.bonappetit.com/recipe/smashed-broccoli-pasta",
    "https://www.bonappetit.com/recipe/classic-pasta-carbonara",
    "https://www.bonappetit.com/recipe/lemon-pepper-wings",
    #"https://www.bonappetit.com/recipe/rigatoni-with-easy-vodka-sauce#intcid=_bon-appetit-recipe-bottom-recirc_9f701f4e-d96d-4792-9f02-1c4967fc2e26_text2vec1_fallback_popular4-2n"
    #anitalianinmykitchen
    "https://anitalianinmykitchen.com/cheese-risotto/",
    "https://anitalianinmykitchen.com/roman-gnocchi-gnocchi-alla-romana/",
    "https://anitalianinmykitchen.com/zucchini-stuffed-tuna/",
    "https://anitalianinmykitchen.com/grilled-tomatoes/",
    "https://anitalianinmykitchen.com/panzanella/",
    "https://anitalianinmykitchen.com/fettuccine-mushrooms/",
    "https://anitalianinmykitchen.com/ricotta-cannelloni/",
    "https://anitalianinmykitchen.com/polenta-gnocchi/",
    "https://anitalianinmykitchen.com/two-bean-soup/",
    "https://anitalianinmykitchen.com/pancetta-asparagus-quiche/",
    "https://anitalianinmykitchen.com/simple-italian-pan-fried-fish/",
    "https://anitalianinmykitchen.com/skillet-artichoke/",
    "https://anitalianinmykitchen.com/lazy-cabbage-rolls/",
    "https://anitalianinmykitchen.com/italian-bean-pancetta-cabbage-soup/",
    "https://anitalianinmykitchen.com/baked-homemade-veggie-burger/",
    "https://anitalianinmykitchen.com/easy-homemade-one-pot-chili/",
    "https://anitalianinmykitchen.com/chickpea-soup/",
    "https://anitalianinmykitchen.com/creamy-broccoli-soup/",
    "https://anitalianinmykitchen.com/creamy-broccoli-bacon-pasta-casserole/",
    "https://anitalianinmykitchen.com/parmesan-crusted-burgers/",
    "https://anitalianinmykitchen.com/tomatoes-stuffed-with-rice/",
    "https://anitalianinmykitchen.com/italian-stuffed-burgers/",
    "https://anitalianinmykitchen.com/asparagus-quiche/",
    "https://anitalianinmykitchen.com/baked-whole-gilt-head-seabream-or-trout/",
    "https://anitalianinmykitchen.com/ricotta-gnocchi/",
    "https://anitalianinmykitchen.com/creamy-italian-pasta-salad/",
    "https://anitalianinmykitchen.com/zucchini-risotto/",
    "https://anitalianinmykitchen.com/simple-italian-meatballs/",
    "https://anitalianinmykitchen.com/pumpkin-fritters/",
    "https://anitalianinmykitchen.com/sicilian-pasta-recipe/",
    "https://anitalianinmykitchen.com/mediterranean-chickpea-salad/",
    "https://anitalianinmykitchen.com/italian-savory-rustic-pie/",
    "https://anitalianinmykitchen.com/zucchini-stuffed-with-meat/",
    "https://anitalianinmykitchen.com/stuffed-meatloaf/",
    "https://anitalianinmykitchen.com/baked-tomatoes/",
    "https://www.bonappetit.com/recipe/oyakodon",
    #"https://www.bonappetit.com/recipe/classic-potato-latkes"
    #allpecepies
    "https://www.allrecipes.com/5-ingredient-salmon-teriyaki-bowls-recipe-11871553",
    "https://www.allrecipes.com/chicken-and-waffle-bites-recipe-11752992",
    "https://www.allrecipes.com/scrambled-hot-dogs-and-eggs-recipe-11754244",
    "https://www.allrecipes.com/4-ingredient-pesto-tortellini-bake-recipe-11748620",
    "https://www.allrecipes.com/recipe/216888/good-new-orleans-creole-gumbo/",
    "https://www.allrecipes.com/recipe/236320/chef-johns-shrimp-etouffee/",
    "https://www.allrecipes.com/cheesy-buldak-ramen-casserole-recipe-11774054",
    "https://www.allrecipes.com/cheesy-lasagna-sheet-pasta-recipe-11703403",
    "https://www.allrecipes.com/recipe/39544/garden-fresh-tomato-soup/",
    "https://www.allrecipes.com/recipe/142382/tim-perrys-soup-creamy-curry-cauliflower-and-broccoli-soup/",
    "https://www.allrecipes.com/recipe/232287/mels-crab-salad/",
    "https://www.allrecipes.com/recipe/14373/greek-salad-i/",
    #acouplecooks
    "https://www.acouplecooks.com/quick-dinner-idea-5-minute-tacos/#tasty-recipes-44382-jump-target",
    "https://www.acouplecooks.com/hummus-bowl/#tasty-recipes-122886-jump-target",
    "https://www.acouplecooks.com/cajun-shrimp/#tasty-recipes-111745-jump-target",
    "https://www.acouplecooks.com/quesadilla-recipe/#tasty-recipes-137895-jump-target",
    "https://www.acouplecooks.com/moroccan-chickpea-stew/#tasty-recipes-17457-jump-target",

]

all_recipes = []

for i in urls:
    response = requests.get(i, headers={'User-Agent': 'Mozilla/5.0'})
    response.raise_for_status()

    scraper = scrape_html(html=response.text, org_url=i)

    recipe = {
        'title': scraper.title(),
        'ingredients': '\n'.join(scraper.ingredients()),
        'instructions': scraper.instructions(),
        'total_time': scraper.total_time(),
        'yields': scraper.yields(),
        'site': i.split('/')[2],
        'image': scraper.image()
    }
    all_recipes.append(recipe)


df = pd.DataFrame(all_recipes)
df.to_csv('recipes_dataset.csv', index=False, encoding='utf-8-sig')
print("готово")