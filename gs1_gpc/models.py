"""
Models for GS1 GPC.

This module provides model classes for GS1 GPC data structures.
"""


class GPCModels:
    """
    Container class for GPC data models.
    
    This class provides access to GPC data structures and their relationships.
    It's used by the process_gpc_xml function to organize and access GPC data.
    """
    
    class Segment:
        """GPC Segment model."""
        
        def __init__(self, code, description):
            """
            Initialize a Segment.
            
            Args:
                code (str): Segment code
                description (str): Segment description
            """
            self.code = code
            self.description = description
            self.families = {}
    
    class Family:
        """GPC Family model."""
        
        def __init__(self, code, description, segment_code):
            """
            Initialize a Family.
            
            Args:
                code (str): Family code
                description (str): Family description
                segment_code (str): Parent segment code
            """
            self.code = code
            self.description = description
            self.segment_code = segment_code
            self.classes = {}
    
    class Class:
        """GPC Class model."""
        
        def __init__(self, code, description, family_code):
            """
            Initialize a Class.
            
            Args:
                code (str): Class code
                description (str): Class description
                family_code (str): Parent family code
            """
            self.code = code
            self.description = description
            self.family_code = family_code
            self.bricks = {}
    
    class Brick:
        """GPC Brick model."""
        
        def __init__(self, code, description, class_code):
            """
            Initialize a Brick.
            
            Args:
                code (str): Brick code
                description (str): Brick description
                class_code (str): Parent class code
            """
            self.code = code
            self.description = description
            self.class_code = class_code
            self.attribute_types = {}
    
    class AttributeType:
        """GPC Attribute Type model."""
        
        def __init__(self, code, description, brick_code):
            """
            Initialize an Attribute Type.
            
            Args:
                code (str): Attribute type code
                description (str): Attribute type description
                brick_code (str): Parent brick code
            """
            self.code = code
            self.description = description
            self.brick_code = brick_code
            self.attribute_values = {}
    
    class AttributeValue:
        """GPC Attribute Value model."""
        
        def __init__(self, code, description, attribute_type_code):
            """
            Initialize an Attribute Value.
            
            Args:
                code (str): Attribute value code
                description (str): Attribute value description
                attribute_type_code (str): Parent attribute type code
            """
            self.code = code
            self.description = description
            self.attribute_type_code = attribute_type_code
    
    def __init__(self):
        """Initialize the GPC models container."""
        self.segments = {}