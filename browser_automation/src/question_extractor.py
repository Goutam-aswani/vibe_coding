import asyncio
import logging
from typing import List, Optional, Dict, Any
from playwright.async_api import Page, ElementHandle
from src.models import FormField, FieldType, ApplicationStep

logger = logging.getLogger(__name__)


class QuestionExtractor:
    """Extracts form fields and questions from LinkedIn Easy Apply modal"""
    
    def __init__(self, page: Page):
        self.page = page
    
    async def get_current_step_info(self) -> Dict[str, Any]:
        """Get information about the current step"""
        try:
            # Try to find step indicator
            step_info = {
                'step_number': 1,
                'step_title': None,
                'total_steps': None
            }
            
            # Look for step indicator (e.g., "1 of 3")
            try:
                step_text = await self.page.locator('[aria-label*="step"]').first.text_content(timeout=2000)
                if step_text:
                    step_info['step_title'] = step_text
            except:
                pass
            
            # Look for progress indicator
            try:
                progress = await self.page.locator('.artdeco-modal__header h2, h3').first.text_content(timeout=2000)
                if progress:
                    step_info['step_title'] = progress
            except:
                pass
            
            return step_info
            
        except Exception as e:
            logger.error(f"Error getting step info: {e}")
            return {'step_number': 1, 'step_title': None, 'total_steps': None}
    
    async def extract_text_inputs(self) -> List[FormField]:
        """Extract text input fields"""
        fields = []
        
        try:
            # Find all input fields in the modal
            inputs = await self.page.locator('.jobs-easy-apply-modal input[type="text"], .jobs-easy-apply-modal input[type="email"], .jobs-easy-apply-modal input[type="tel"], .jobs-easy-apply-modal input[type="number"]').all()
            
            for idx, input_elem in enumerate(inputs):
                try:
                    # Get attributes
                    field_id = await input_elem.get_attribute('id') or f"text_input_{idx}"
                    field_name = await input_elem.get_attribute('name') or ""
                    placeholder = await input_elem.get_attribute('placeholder') or ""
                    required = await input_elem.get_attribute('required') is not None
                    current_value = await input_elem.input_value()
                    input_type = await input_elem.get_attribute('type') or "text"
                    
                    # Find label
                    label_text = ""
                    try:
                        # Try to find associated label
                        label = await self.page.locator(f'label[for="{field_id}"]').first.text_content(timeout=1000)
                        if label:
                            label_text = label.strip()
                    except:
                        # Try to find parent label
                        try:
                            parent_label = await input_elem.locator('xpath=ancestor::label').first.text_content(timeout=1000)
                            if parent_label:
                                label_text = parent_label.strip()
                        except:
                            pass
                    
                    # If no label found, use placeholder or name
                    if not label_text:
                        label_text = placeholder or field_name or f"Field {idx + 1}"
                    
                    # Determine field type
                    field_type_map = {
                        'email': FieldType.EMAIL,
                        'tel': FieldType.PHONE,
                        'number': FieldType.NUMBER,
                        'text': FieldType.TEXT
                    }
                    
                    field = FormField(
                        field_id=field_id,
                        field_type=field_type_map.get(input_type, FieldType.TEXT),
                        label=label_text,
                        placeholder=placeholder or None,
                        required=required,
                        current_value=current_value or None
                    )
                    
                    fields.append(field)
                    logger.info(f"Extracted text field: {label_text}")
                    
                except Exception as e:
                    logger.error(f"Error extracting text input: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error finding text inputs: {e}")
        
        return fields
    
    async def extract_textareas(self) -> List[FormField]:
        """Extract textarea fields"""
        fields = []
        
        try:
            textareas = await self.page.locator('.jobs-easy-apply-modal textarea').all()
            
            for idx, textarea in enumerate(textareas):
                try:
                    field_id = await textarea.get_attribute('id') or f"textarea_{idx}"
                    placeholder = await textarea.get_attribute('placeholder') or ""
                    required = await textarea.get_attribute('required') is not None
                    current_value = await textarea.input_value()
                    
                    # Find label
                    label_text = ""
                    try:
                        label = await self.page.locator(f'label[for="{field_id}"]').first.text_content(timeout=1000)
                        if label:
                            label_text = label.strip()
                    except:
                        pass
                    
                    if not label_text:
                        label_text = placeholder or f"Text Area {idx + 1}"
                    
                    field = FormField(
                        field_id=field_id,
                        field_type=FieldType.TEXTAREA,
                        label=label_text,
                        placeholder=placeholder or None,
                        required=required,
                        current_value=current_value or None
                    )
                    
                    fields.append(field)
                    logger.info(f"Extracted textarea: {label_text}")
                    
                except Exception as e:
                    logger.error(f"Error extracting textarea: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error finding textareas: {e}")
        
        return fields
    
    async def extract_select_fields(self) -> List[FormField]:
        """Extract dropdown/select fields"""
        fields = []
        
        try:
            # Standard select elements
            selects = await self.page.locator('.jobs-easy-apply-modal select').all()
            
            for idx, select in enumerate(selects):
                try:
                    field_id = await select.get_attribute('id') or f"select_{idx}"
                    required = await select.get_attribute('required') is not None
                    
                    # Get options
                    options = []
                    option_elements = await select.locator('option').all()
                    for option in option_elements:
                        option_text = await option.text_content()
                        if option_text and option_text.strip():
                            options.append(option_text.strip())
                    
                    # Get current value
                    current_value = await select.input_value()
                    
                    # Find label
                    label_text = ""
                    try:
                        label = await self.page.locator(f'label[for="{field_id}"]').first.text_content(timeout=1000)
                        if label:
                            label_text = label.strip()
                    except:
                        pass
                    
                    if not label_text:
                        label_text = f"Dropdown {idx + 1}"
                    
                    field = FormField(
                        field_id=field_id,
                        field_type=FieldType.SELECT,
                        label=label_text,
                        required=required,
                        options=options,
                        current_value=current_value or None
                    )
                    
                    fields.append(field)
                    logger.info(f"Extracted select field: {label_text} with {len(options)} options")
                    
                except Exception as e:
                    logger.error(f"Error extracting select: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error finding selects: {e}")
        
        return fields
    
    async def extract_radio_buttons(self) -> List[FormField]:
        """Extract radio button groups"""
        fields = []
        
        try:
            # Find radio button groups by name
            radio_groups = {}
            radios = await self.page.locator('.jobs-easy-apply-modal input[type="radio"]').all()
            
            for radio in radios:
                try:
                    name = await radio.get_attribute('name')
                    if not name:
                        continue
                    
                    if name not in radio_groups:
                        radio_groups[name] = []
                    
                    value = await radio.get_attribute('value') or ""
                    checked = await radio.is_checked()
                    
                    # Try to find label for this radio
                    radio_id = await radio.get_attribute('id')
                    label_text = value
                    
                    if radio_id:
                        try:
                            label = await self.page.locator(f'label[for="{radio_id}"]').first.text_content(timeout=1000)
                            if label:
                                label_text = label.strip()
                        except:
                            pass
                    
                    radio_groups[name].append({
                        'value': value,
                        'label': label_text,
                        'checked': checked
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing radio button: {e}")
                    continue
            
            # Create FormField for each radio group
            for idx, (group_name, radios) in enumerate(radio_groups.items()):
                try:
                    options = [r['label'] for r in radios]
                    current_value = next((r['label'] for r in radios if r['checked']), None)
                    
                    # Try to find group label
                    group_label = group_name
                    try:
                        # Look for fieldset legend or preceding label
                        fieldset = await self.page.locator(f'fieldset:has(input[name="{group_name}"])').first
                        legend = await fieldset.locator('legend').first.text_content(timeout=1000)
                        if legend:
                            group_label = legend.strip()
                    except:
                        pass
                    
                    field = FormField(
                        field_id=group_name,
                        field_type=FieldType.RADIO,
                        label=group_label,
                        required=False,
                        options=options,
                        current_value=current_value
                    )
                    
                    fields.append(field)
                    logger.info(f"Extracted radio group: {group_label} with {len(options)} options")
                    
                except Exception as e:
                    logger.error(f"Error creating radio field: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error finding radio buttons: {e}")
        
        return fields
    
    async def extract_checkboxes(self) -> List[FormField]:
        """Extract checkbox fields"""
        fields = []
        
        try:
            checkboxes = await self.page.locator('.jobs-easy-apply-modal input[type="checkbox"]').all()
            
            for idx, checkbox in enumerate(checkboxes):
                try:
                    field_id = await checkbox.get_attribute('id') or f"checkbox_{idx}"
                    name = await checkbox.get_attribute('name') or field_id
                    checked = await checkbox.is_checked()
                    
                    # Find label
                    label_text = ""
                    try:
                        label = await self.page.locator(f'label[for="{field_id}"]').first.text_content(timeout=1000)
                        if label:
                            label_text = label.strip()
                    except:
                        pass
                    
                    if not label_text:
                        label_text = f"Checkbox {idx + 1}"
                    
                    field = FormField(
                        field_id=field_id,
                        field_type=FieldType.CHECKBOX,
                        label=label_text,
                        required=False,
                        current_value="checked" if checked else "unchecked"
                    )
                    
                    fields.append(field)
                    logger.info(f"Extracted checkbox: {label_text}")
                    
                except Exception as e:
                    logger.error(f"Error extracting checkbox: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error finding checkboxes: {e}")
        
        return fields
    
    async def extract_file_inputs(self) -> List[FormField]:
        """Extract file upload fields"""
        fields = []
        
        try:
            file_inputs = await self.page.locator('.jobs-easy-apply-modal input[type="file"]').all()
            
            for idx, file_input in enumerate(file_inputs):
                try:
                    field_id = await file_input.get_attribute('id') or f"file_{idx}"
                    accept = await file_input.get_attribute('accept') or ""
                    
                    # Find label
                    label_text = ""
                    try:
                        label = await self.page.locator(f'label[for="{field_id}"]').first.text_content(timeout=1000)
                        if label:
                            label_text = label.strip()
                    except:
                        pass
                    
                    if not label_text:
                        label_text = f"File Upload {idx + 1}"
                    
                    field = FormField(
                        field_id=field_id,
                        field_type=FieldType.FILE,
                        label=label_text,
                        required=False,
                        hint=f"Accepted formats: {accept}" if accept else None
                    )
                    
                    fields.append(field)
                    logger.info(f"Extracted file input: {label_text}")
                    
                except Exception as e:
                    logger.error(f"Error extracting file input: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error finding file inputs: {e}")
        
        return fields
    
    async def extract_all_fields(self) -> List[FormField]:
        """Extract all form fields from the current step"""
        all_fields = []
        
        logger.info("Extracting all form fields...")
        
        # Extract all field types
        text_fields = await self.extract_text_inputs()
        all_fields.extend(text_fields)
        
        textareas = await self.extract_textareas()
        all_fields.extend(textareas)
        
        selects = await self.extract_select_fields()
        all_fields.extend(selects)
        
        radios = await self.extract_radio_buttons()
        all_fields.extend(radios)
        
        checkboxes = await self.extract_checkboxes()
        all_fields.extend(checkboxes)
        
        file_inputs = await self.extract_file_inputs()
        all_fields.extend(file_inputs)
        
        logger.info(f"Extracted {len(all_fields)} total fields")
        return all_fields
    
    async def check_has_next_step(self) -> bool:
        """Check if there's a 'Next' button (more steps)"""
        try:
            # Look for Next/Continue button
            next_button = await self.page.locator('button[aria-label*="Continue"], button[aria-label*="next step"], button:has-text("Next"), button:has-text("Continue")').first.is_visible(timeout=2000)
            return next_button
        except:
            return False
    
    async def check_has_review_button(self) -> bool:
        """Check if there's a 'Review' button (last step before submit)"""
        try:
            review_button = await self.page.locator('button[aria-label*="Review"], button:has-text("Review")').first.is_visible(timeout=2000)
            return review_button
        except:
            return False
