\# AI Data Analyst Agent



An application-independent data analysis platform that allows users to upload SQL databases and query them using natural language.



The system dynamically inspects the uploaded database schema, generates SQL queries using Groq, validates the generated SQL, executes read-only queries against MySQL, performs statistical and anomaly analysis, generates visualizations, and produces concise analytical insights.



\## Features



\- Upload SQL databases containing schema and data

\- Dynamic schema discovery

\- Application-independent database analysis

\- Natural language database queries

\- Conversational follow-up questions

\- Groq-powered query planning

\- Automatic SQL generation

\- SQL validation and read-only execution

\- Automatic SQL error correction

\- Statistical analysis

\- IQR-based anomaly detection

\- Automatic chart selection

\- Bar, line, pie and scatter visualizations

\- Session-based database management

\- FastAPI backend

\- Streamlit frontend

\- MySQL database engine

\- Interactive API documentation through FastAPI

\- No hardcoded application-specific table structure



\## Architecture



```text

&#x20;                       Streamlit

&#x20;                           |

&#x20;                           v

&#x20;                    SQL File Upload

&#x20;                           |

&#x20;                           v

&#x20;                        FastAPI

&#x20;                           |

&#x20;                           v

&#x20;                   SQL Importer

&#x20;                           |

&#x20;                           v

&#x20;                Temporary MySQL Database

&#x20;                           |

&#x20;                      Session ID

&#x20;                           |

&#x20;                           v

&#x20;                   Question Rewriter

&#x20;                           |

&#x20;                           v

&#x20;                Dynamic Schema Inspector

&#x20;                           |

&#x20;                           v

&#x20;                    Groq Planner

&#x20;                           |

&#x20;             +-------------+-------------+

&#x20;             |                           |

&#x20;             v                           v

&#x20;       SQL Generator              Analysis Plan

&#x20;             |                           |

&#x20;             v                           |

&#x20;       SQL Validator                     |

&#x20;             |                           |

&#x20;             v                           |

&#x20;       SQL Execution                     |

&#x20;             |                           |

&#x20;             +-------------+-------------+

&#x20;                           |

&#x20;                           v

&#x20;                   Analysis Engine

&#x20;                           |

&#x20;             +-------------+-------------+

&#x20;             |             |             |

&#x20;             v             v             v

&#x20;        Statistics     Anomalies      Charts

&#x20;             |             |             |

&#x20;             +-------------+-------------+

&#x20;                           |

&#x20;                           v

&#x20;                    Groq Insight

&#x20;                           |

&#x20;                           v

&#x20;                        FastAPI

&#x20;                           |

&#x20;                           v

&#x20;                       Streamlit

