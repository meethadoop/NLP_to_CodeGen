import openai
from typing import Dict, Any, Optional, List
import time
from .utils.logger import get_logger
from .database.manager import DatabaseManager

logger = get_logger(__name__)

class QueryTemplate:
    def __init__(self, name: str, description: str, template: str, parameters: List[str]):
        self.name = name
        self.description = description
        self.template = template
        self.parameters = parameters
        self.usage_count = 0
        self.last_used = None

class TemplateManager:
    def __init__(self):
        self.templates: Dict[str, QueryTemplate] = {}
    
    def add_template(self, name: str, description: str, template: str, parameters: List[str]):
        self.templates[name] = QueryTemplate(name, description, template, parameters)
    
    def get_template(self, name: str) -> QueryTemplate:
        if name not in self.templates:
            raise ValueError(f"Template '{name}' not found")
        return self.templates[name]
    
    def list_templates(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
                "usage_count": t.usage_count
            }
            for t in self.templates.values()
        ]

class NLSQL:
    def __init__(self, config):
        self.config = config
        self.template_manager = TemplateManager()
        DatabaseManager.initialize(config.db_path)
        self.db = DatabaseManager.get_instance()
        openai.api_key = config.openai_api_key
        
    async def generate_sql(self, query: str) -> str:
        """Generate SQL from natural language using OpenAI"""
        try:
            # Get database schema
            schema = self.db.get_schema()
            schema_description = "Available tables:\n"
            for table, columns in schema.items():
                schema_description += f"- {table} ({', '.join(columns)})\n"
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"""You are a SQL expert. 
                     {schema_description}
                     Convert natural language queries to SQL. 
                     Only respond with the SQL query, no explanations."""},
                    {"role": "user", "content": query}
                ],
                temperature=0.1,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            raise Exception(f"Failed to generate SQL: {str(e)}")
        
    async def process_query(self, query: str, use_cache: bool = True) -> Dict[str, Any]:
        """Process a natural language query"""
        start_time = time.time()
        
        try:
            sql_query = await self.generate_sql(query)
            results = self.db.execute_query(sql_query)
            
            execution_time = time.time() - start_time
            
            return {
                "query": query,
                "sql": sql_query,
                "results": results,
                "metadata": {
                    "cached": use_cache,
                    "execution_time": round(execution_time, 3),
                    "row_count": len(results)
                }
            }
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise

    async def process_template(self, template_name: str, parameters: Dict[str, str]) -> Dict[str, Any]:
        """Process a query using a template"""
        try:
            template = self.template_manager.get_template(template_name)
            
            # Validate all required parameters are provided
            missing_params = set(template.parameters) - set(parameters.keys())
            if missing_params:
                raise ValueError(f"Missing required parameters: {missing_params}")
            
            # Replace parameters in template
            query = template.template
            for param_name, param_value in parameters.items():
                query = query.replace(f"{{{param_name}}}", param_value)
            
            # Update template usage statistics
            template.usage_count += 1
            template.last_used = time.time()
            
            return await self.process_query(query, use_cache=True)
            
        except Exception as e:
            logger.error(f"Template processing error: {str(e)}")
            raise
    
    def add_query_template(self, name: str, description: str, template: str, parameters: list):
        """Add a new query template"""
        try:
            self.template_manager.add_template(name, description, template, parameters)
            logger.info(f"Added new template: {name}")
        except Exception as e:
            logger.error(f"Error adding template: {str(e)}")
            raise
    
    def get_query_statistics(self) -> Dict[str, Any]:
        """Get query execution statistics"""
        templates = self.template_manager.list_templates()
        total_usage = sum(t["usage_count"] for t in templates)
        
        return {
            "total_templates": len(templates),
            "total_template_usage": total_usage,
            "templates": templates
        }

    def close(self):
        """Cleanup resources"""
        pass
