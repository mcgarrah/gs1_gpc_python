"""
Callbacks for GS1 GPC processing.

This module provides callback classes for GS1 GPC data processing events.
"""


class GPCProcessedCallback:
    """
    Callback interface for GPC XML processing events.
    
    This class defines the interface for callbacks that can be triggered
    during GPC XML processing. Subclass this to implement custom behavior
    when GPC data is processed.
    """
    
    def on_segment_processed(self, segment_code, segment_desc, is_new):
        """
        Called when a segment is processed.
        
        Args:
            segment_code (str): Segment code
            segment_desc (str): Segment description
            is_new (bool): True if this is a new segment, False if it already existed
        """
        pass
    
    def on_family_processed(self, family_code, family_desc, segment_code, is_new):
        """
        Called when a family is processed.
        
        Args:
            family_code (str): Family code
            family_desc (str): Family description
            segment_code (str): Parent segment code
            is_new (bool): True if this is a new family, False if it already existed
        """
        pass
    
    def on_class_processed(self, class_code, class_desc, family_code, is_new):
        """
        Called when a class is processed.
        
        Args:
            class_code (str): Class code
            class_desc (str): Class description
            family_code (str): Parent family code
            is_new (bool): True if this is a new class, False if it already existed
        """
        pass
    
    def on_brick_processed(self, brick_code, brick_desc, class_code, is_new):
        """
        Called when a brick is processed.
        
        Args:
            brick_code (str): Brick code
            brick_desc (str): Brick description
            class_code (str): Parent class code
            is_new (bool): True if this is a new brick, False if it already existed
        """
        pass
    
    def on_attribute_type_processed(self, att_type_code, att_type_text, brick_code, is_new):
        """
        Called when an attribute type is processed.
        
        Args:
            att_type_code (str): Attribute type code
            att_type_text (str): Attribute type description
            brick_code (str): Parent brick code
            is_new (bool): True if this is a new attribute type, False if it already existed
        """
        pass
    
    def on_attribute_value_processed(self, att_value_code, att_value_text, att_type_code, is_new):
        """
        Called when an attribute value is processed.
        
        Args:
            att_value_code (str): Attribute value code
            att_value_text (str): Attribute value description
            att_type_code (str): Parent attribute type code
            is_new (bool): True if this is a new attribute value, False if it already existed
        """
        pass
    
    def on_processing_complete(self, counters):
        """
        Called when processing is complete.
        
        Args:
            counters (dict): Dictionary with processing statistics
        """
        pass