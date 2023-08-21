function [masking Mask] = timeMultiplexing(inputSequence,sequenceLength,nodes,maskingType, maskingOffset)

switch(maskingType)
   
    case 'hold' % Sample and Hold

        masking = repelem (inputSequence,nodes);
        
    case 'binary' % Binary Weight Masking
        
        AinputSequence = repelem (inputSequence,nodes);
        rng('default');
        Mask = 2* randi(2,nodes,1)-1 -2;
        Amasking = repmat(Mask,sequenceLength,1);
        
        if contains(maskingOffset, 'true')    
            % Offset
            masking = (Amasking + 1) .* AinputSequence;
        else
            % No-Offset
            masking = Amasking .* AinputSequence; % u * M
        end

    case 'random' % Random Weight Masking
        
        AinputSequence = repelem (inputSequence,nodes);
        %rng('default');
        Mask = -1 + (1+1)*rand(nodes,1);
        Amasking = repmat(Mask,sequenceLength,1);
        
        if contains(maskingOffset, 'true') 
            % Offset
             masking = (Amasking + 1) .* AinputSequence;
        else
            % No-Offset
            masking = Amasking .* AinputSequence; % M * u
        end
        
        otherwise
        
        masking = [];

end