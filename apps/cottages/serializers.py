from rest_framework import serializers
from .models import Cottage, CottageImage, Amenity, CottageAmenity


class AmenitySerializer(serializers.ModelSerializer):
    """Сериализатор для удобств"""
    
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'icon']


class CottageImageSerializer(serializers.ModelSerializer):
    """Сериализатор для изображений коттеджа"""
    
    class Meta:
        model = CottageImage
        fields = ['id', 'image', 'is_primary', 'order']


class CottageSerializer(serializers.ModelSerializer):
    """Сериализатор для списка коттеджей"""
    primary_image = serializers.SerializerMethodField()
    amenities = AmenitySerializer(source='amenities.amenity', many=True, read_only=True)
    
    class Meta:
        model = Cottage
        fields = ['id', 'name', 'description', 'address', 'capacity', 
                 'price_per_night', 'primary_image', 'amenities']
    
    def get_primary_image(self, obj):
        primary_img = obj.images.filter(is_primary=True).first()
        if primary_img:
            return primary_img.image.url
        # Если нет основного изображения, берем первое
        first_img = obj.images.first()
        return first_img.image.url if first_img else None


class CottageDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации о коттедже"""
    images = CottageImageSerializer(many=True, read_only=True)
    amenities = AmenitySerializer(source='amenities.amenity', many=True, read_only=True)
    
    class Meta:
        model = Cottage
        fields = ['id', 'name', 'description', 'address', 'capacity', 
                 'price_per_night', 'images', 'amenities', 'created_at', 'updated_at']
