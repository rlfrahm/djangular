__author__ = 'kurt'

from haystack import indexes
from haystack.indexes import FacetMultiValueField, SearchIndex

from django.template.defaultfilters import  slugify
from recipes.models import Recipe, Food, Ingredient


class RecipeIndex(SearchIndex, indexes.Indexable):
   text = indexes.CharField(document=True, use_template=True)
   title = indexes.CharField(model_attr='title', faceted= True)
   ingredient = indexes.MultiValueField(null=True)

   description = indexes.CharField(model_attr='description', faceted=True)
    content = indexes.EdgeNgramField(model_attr='ingredient')

   def get_model(self):
       return Recipe

   def index__all_queryset(self):

       """
       Used when the entire index for model is updated.
       """
       return Recipe.objects.all().select_related()


#class FoodIndex(indexes.SearchIndex, indexes.Indexable):
#    text = indexes.CharField(document=True, use_template=True)
#    # name = indexes.CharField(model_attr='name')
#    #content = indexes.EdgeNgramField(model_attr='ingredient')
#    content = indexes.EdgeNgramField(model_attr='name')
#
#    def get_model(self):
#        return Food
#
#
#    def index_queryset(self, using=None):
#        """
#        Used when the entire index for model is updated.
#        """
#        return self.get_model().objects.all()


class IngredientIndex(SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    direction = indexes.CharField(model_attr='direction', faceted=True)
    recipe = indexes.CharField(model_attr='recipe', faceted=True)
    food = indexes.CharField(model_attr='food', faceted=True)
    # foods = indexes.FacetMultiValueField()
    content_auto = indexes.EdgeNgramField(model_attr='food')


    def get_model(self):
        return Ingredient

    def prepare_recipe(self, obj):

        recipe = u'sqs1|sqs2|sqs3|sqs4'

        if 'recipe' in self.prepared_data:

            food_bits = self.prepared_data['recipe'].split()

            recipe = "%s, %s" %(food_bits[-1], ''.join(food_bits[: -1]))
        return recipe



    # def index_queryset(self, using=None):
    #     """
    #     Used when the entire index for model is updated.
    #     """
    #     return self.get_model().objects.all()
