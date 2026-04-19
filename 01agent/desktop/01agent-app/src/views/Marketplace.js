import React, { useState, useEffect } from 'react';
import { useSelector } from 'react-redux';
import styled from 'styled-components';
import theme from '../theme/GlobalTheme';
import { Card, Button, Badge } from '../components/UI/SuperiorComponents';
import { MdShop, MdDownload, MdStar, MdSearch } from 'react-icons/md';
import axios from '../utils/axios';

const MarketplaceContainer = styled.div`
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
`;

const Title = styled.h1`
  font-size: 2.5rem;
  font-weight: 800;
  color: ${props => props.isDarkMode ? theme.colors.dark.text : theme.colors.light.text};
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const SearchBar = styled.div`
  display: flex;
  align-items: center;
  background: ${props => props.isDarkMode ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'};
  border: 1px solid ${props => props.isDarkMode ? theme.colors.dark.border : theme.colors.light.border};
  border-radius: ${theme.radius.md};
  padding: 0.5rem 1rem;
  width: 400px;

  input {
    background: transparent;
    border: none;
    color: inherit;
    padding: 0.5rem;
    width: 100%;
    outline: none;
  }
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
`;

const SkillCard = styled(Card)`
  display: flex;
  flex-direction: column;
  height: 100%;
`;

const SkillInfo = styled.div`
  flex: 1;
  margin-bottom: 1.5rem;

  h3 {
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
  }

  p {
    font-size: 0.9rem;
    color: ${props => props.isDarkMode ? theme.colors.dark.textSecondary : theme.colors.light.textSecondary};
    line-height: 1.4;
  }
`;

const SkillStats = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: ${props => props.isDarkMode ? theme.colors.dark.textMuted : theme.colors.light.textMuted};
  margin-top: auto;
`;

export default function Marketplace() {
  const isDarkMode = useSelector(state => state.isDarkMode);
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSkills = async () => {
      try {
        const response = await axios.get('/skills/marketplace');
        setSkills(response.data);
      } catch (err) {
        console.error("Failed to fetch skills", err);
      } finally {
        setLoading(false);
      }
    };
    fetchSkills();
  }, []);

  return (
    <MarketplaceContainer>
      <Header>
        <Title isDarkMode={isDarkMode}>
          <MdShop /> Skill Marketplace
        </Title>
        <SearchBar isDarkMode={isDarkMode}>
          <MdSearch size={20} />
          <input placeholder="Search for automation skills..." />
        </SearchBar>
      </Header>

      <Grid>
        {loading ? (
          <p>Loading skills...</p>
        ) : skills.length === 0 ? (
          <p>No skills found in the marketplace yet.</p>
        ) : (
          skills.map(skill => (
            <SkillCard key={skill.id} isDarkMode={isDarkMode} hover>
              <SkillInfo isDarkMode={isDarkMode}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <h3>{skill.name}</h3>
                  <Badge variant="primary">{skill.category || 'General'}</Badge>
                </div>
                <p>{skill.description}</p>
              </SkillInfo>
              <SkillStats isDarkMode={isDarkMode}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <MdStar color="#FFD700" /> {skill.rating || '4.8'}
                </div>
                <div>{skill.usage_count || 0} installs</div>
              </SkillStats>
              <Button
                variant="primary"
                fullWidth
                style={{ marginTop: '1rem' }}
              >
                <MdDownload /> Install Skill
              </Button>
            </SkillCard>
          ))
        )}
      </Grid>
    </MarketplaceContainer>
  );
}
