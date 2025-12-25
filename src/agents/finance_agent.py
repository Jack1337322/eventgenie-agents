from chains.budget_chain import BudgetChain
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class FinanceAgent:
    """
    Finance Agent - calculates budgets using GigaChat with budget constraints
    """
    
    def __init__(self):
        self.chain = BudgetChain()
        logger.info("Finance Agent initialized")
    
    async def calculate_budget(self, event_data: dict) -> dict:
        """
        Calculate event budget with budget constraints
        
        Args:
            event_data: Dictionary containing event information including:
                - event_name: str
                - total_budget: float (общий бюджет, который нельзя превышать)
                - event_type: str
                - participant_count: int
                - duration_hours: int
                - venue_type: str
                - date: str
                - priority_categories: List[str] (приоритетные категории расходов)
                - budget_constraints: Dict[str, float] (ограничения по категориям)
                
        Returns:
            dict: Budget with detailed categories, total, analysis, and recommendations
                Structure:
                - categories: List[Dict] - детальные категории расходов
                - total_cost: float - общая стоимость
                - budget_status: str - статус бюджета (в рамках/превышен)
                - analysis: str - анализ бюджета
                - recommendations: List[str] - рекомендации по оптимизации
                - category_details: Dict[str, Dict] - детальная информация по категориям
        """
        try:
            logger.info(f"Finance Agent: Calculating budget for {event_data.get('event_name')}")
            
            # Проверяем наличие общего бюджета
            total_budget = event_data.get('total_budget')
            if total_budget is None:
                logger.warning("Total budget not specified, calculations may exceed reasonable limits")
            
            # Добавляем информацию о приоритетах и ограничениях
            enhanced_event_data = event_data.copy()
            
            # Если есть ограничения по бюджету, добавляем их в запрос
            if 'budget_constraints' not in enhanced_event_data:
                enhanced_event_data['budget_constraints'] = {}
            
            # Добавляем общий бюджет в constraints
            if total_budget:
                enhanced_event_data['budget_constraints']['total'] = total_budget
            
            result = await self.chain.calculate_budget(enhanced_event_data)
            
            # Проверяем, не превышен ли бюджет
            if total_budget and 'total_cost' in result:
                total_cost = result['total_cost']
                if total_cost > total_budget:
                    result['budget_status'] = 'exceeded'
                    overspend = total_cost - total_budget
                    
                    # Добавляем рекомендации по сокращению расходов
                    if 'recommendations' not in result:
                        result['recommendations'] = []
                    result['recommendations'].append(
                        f"⚠️ Бюджет превышен на {overspend:.2f} руб. Рекомендуется сократить расходы."
                    )
                    
                    # Детализируем категории для оптимизации
                    if 'category_details' in result:
                        # Сортируем категории по убыванию стоимости для выявления самых затратных
                        sorted_categories = sorted(
                            result['category_details'].items(),
                            key=lambda x: x[1].get('amount', 0),
                            reverse=True
                        )
                        
                        top_categories = [cat[0] for cat in sorted_categories[:3]]
                        if top_categories:
                            result['recommendations'].append(
                                f"Наибольшие расходы в категориях: {', '.join(top_categories)}. "
                                f"Рассмотрите возможность оптимизации этих статей расходов."
                            )
                else:
                    result['budget_status'] = 'within_budget'
                    remaining = total_budget - total_cost
                    result['recommendations'].append(
                        f"✅ Бюджет в пределах лимита. Остаток: {remaining:.2f} руб."
                    )
            
            # Обеспечиваем детализацию категорий
            if 'categories' in result and isinstance(result['categories'], list):
                detailed_categories = []
                for i, category in enumerate(result['categories']):
                    if isinstance(category, dict):
                        # Дополняем информацию о категории
                        detailed_category = {
                            'id': i + 1,
                            'name': category.get('name', f'Категория {i+1}'),
                            'description': category.get('description', ''),
                            'amount': category.get('amount', 0),
                            'percentage': category.get('percentage', 0),
                            'subcategories': category.get('subcategories', []),
                            'priority': category.get('priority', 'medium'),
                            'notes': category.get('notes', ''),
                            'is_flexible': category.get('is_flexible', True)
                        }
                        detailed_categories.append(detailed_category)
                
                result['detailed_categories'] = detailed_categories
                
                # Добавляем детальную сводку по категориям
                if 'analysis' not in result:
                    result['analysis'] = ''
                
                category_summary = "\nДетализация расходов по категориям:\n"
                for cat in detailed_categories:
                    category_summary += (
                        f"{cat['id']}. {cat['name']}: {cat['amount']:.2f} руб. "
                        f"({cat['percentage']:.1f}% бюджета)\n"
                    )
                    if cat.get('subcategories'):
                        for sub in cat['subcategories']:
                            if isinstance(sub, dict):
                                category_summary += f"   - {sub.get('name')}: {sub.get('amount', 0):.2f} руб.\n"
                
                result['analysis'] += category_summary
            
            logger.info(f"Finance Agent: Budget calculated successfully. "
                       f"Status: {result.get('budget_status', 'unknown')}")
            
            # Добавляем временные метки для отслеживания
            result['calculation_timestamp'] = datetime.datetime.now().isoformat()
            result['budget_version'] = '1.0'
            
            return result
            
        except Exception as e:
            logger.error(f"Finance Agent error: {e}", exc_info=True)
            # Возвращаем структурированную ошибку
            return {
                'error': str(e),
                'categories': [],
                'total_cost': 0,
                'budget_status': 'error',
                'analysis': 'Произошла ошибка при расчете бюджета',
                'recommendations': ['Обратитесь к администратору системы'],
                'detailed_categories': []
            }

# Добавляем импорт datetime для временных меток
import datetime
